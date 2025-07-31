import os

import requests
from celery import shared_task
from django.db import connection
from datetime import datetime

from movies.service.movie import MovieService

movie_service = MovieService()

tmdb_key = os.environ("TMDB_API_KEY")
tmdb_url = os.environ("TMDB_URL")


@shared_task
def fetch_and_store_movies():
    url = f"{tmdb_url}/3/movie/now_playing"
    params = {
        "api_key": tmdb_key,
        "language": "en-US",
        "page": 1,
    }

    try:
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        movies = response.json().get("results", [])
    except Exception as e:
        print(f"Error {e}")
        return

    if not movies:
        return

    is_inserted = movie_service.insert_movies(movies)

    if not is_inserted:
        print("f[ERROR]: Movies not inserted!")
        return
    print("Movies inserted correctly")
