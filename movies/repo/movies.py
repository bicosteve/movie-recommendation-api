from django.db import connection, transaction, IntegrityError, DatabaseError


class MovieRepository:
    def __init__(self):
        self.cursor = connection.cursor()

    def add_movies(self, movies):
        for movie in movies:
            try:
                tmdb_id = movie[id]
                title = movie["title"]
                overview = movie.get("overview", "")
                genres = ",".join(str(id) for gid in movie.get("genre_ids", []))
                release_date = movie.get("release_date")
                poster_url = movie.get("poster_path")

                q = """
                    INSERT INTO movies (tmdb_id,title,overview,genres,release_date,poster_url)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;
                """

                self.cursor.execute(
                    q, [tmdb_id, title, overview, genres, release_date, poster_url]
                )
                return True

            except Exception as e:
                print(f"MOVIES: failed to insert movie {title} because of {e}")
                return False
