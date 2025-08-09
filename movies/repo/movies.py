import os
from django.db import IntegrityError, DatabaseError
from movies.models import Movie


class MovieRepository:
    def __init__(self, base_poster_url):
        self.base_poster_url = base_poster_url

    def add_movie(self, movies):
        for movie in movies:
            try:
                tmdb_id = movie["id"]
                title = movie["original_name"]
                overview = movie.get("overview", "")
                genres = ",".join(str(gid) for gid in movie.get("genre_ids", []))
                release_date = movie.get("first_air_date")
                poster_path = movie.get("poster_path", "")
                poster_url = (
                    f"{self.base_poster_url}{poster_path}" if poster_path else ""
                )

                object, created = Movie.objects.get_or_create(
                    tmdb_id=tmdb_id,
                    defaults={
                        "title": title,
                        "overview": overview,
                        "genres": genres,
                        "release_date": release_date,
                        "poster_url": poster_url,
                    },
                )

                return {
                    "id": tmdb_id,
                    "title": title,
                    "status": "created" if created else "exists",
                }
            except IntegrityError as e:
                return {
                    "id": tmdb_id,
                    "title": title,
                    "status": "failed",
                    "error": str(e),
                }
