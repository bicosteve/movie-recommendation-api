import os
import logging

import requests
from celery import shared_task

from movies.service.movie import MovieService

logger = logging.getLogger(__name__)
movie_service = MovieService()


tmdb_key = os.getenv("TMDB_API_KEY")
tmdb_url = os.getenv("TMDB_URL")


@shared_task
def fetch_and_store_movies():
    if not tmdb_key or not tmdb_url:
        logger.error("TMDB credentials or URL missing from environment.")
        return

    all_movies = []

    for page in range(1, 3):
        # "/movie?include_adult=true&include_video=true&language=en-US&page=1&sort_by=popularity.desc"
        url = f"{tmdb_url}/3/movie/discover?"
        params = {
            "incldue_adult": "true",
            "include_video": "true",
            "language": "en-US",
            "page": page,
            "sort_by": "popularity.desc",
        }

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {tmdb_key}",
        }

        try:
            response = requests.get(url=url, params=params, headers=headers)
            response.raise_for_status()
            movies = response.json().get("results", [])

            if movies:
                all_movies.extend(movies)
            else:
                logger.info(f"No movies found on the page {page}")
        except Exception as e:
            logger.exception(f"Unexpected error on page {page}: {str(e)}")
            return

    if not all_movies:
        logger.warning("No movies fetched form TMDB on all pages")
        return

    service = MovieService()
    result = service.insert_movies(all_movies)
    if result["failed"] > 0:
        logger.warning(f"{result['failed']} movie(s) failed to insert")
    else:
        logger.info(f"All {result['inserted']} movies inserted successfully")
