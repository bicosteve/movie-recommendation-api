import os


from django.db import connection, transaction, IntegrityError, DatabaseError


class MovieRepository:
    def __init__(self):
        self.cursor = connection.cursor()
        self.base_poster_url = os.getenv("TMDB_BASE_IMG_URL")

    def add_movies(self, movies):
        results = []
        for movie in movies:
            try:
                tmdb_id = movie["id"]
                title = movie["original_name"]
                overview = movie.get("overview", "")
                genres = ",".join(str(gid) for gid in movie.get("genre_ids", []))
                release_date = movie.get("first_air_date")
                poster_url = f'{self.base_poster_url}{movie.get("poster_path",'')}'

                if len(genres) < 1:
                    genres = tmdb_id

                if len(overview) < 1:
                    overview = title

                q = """
                    INSERT INTO movies (tmdb_id,title,overview,genres,release_date,poster_url)
                    VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;
                """

                self.cursor.execute(
                    q, [tmdb_id, title, overview, genres, release_date, poster_url]
                )
                results.append(
                    {
                        "id": tmdb_id,
                        "title": title,
                        "status": "success",
                    }
                )
            except Exception as e:
                print(
                    f"[ERROR] Failed to insert movie `{movie.get('title','UNKNOWN')}`, `ID->{movie.get('id','N/A')}` because of {e}"
                )
                results.append(
                    {
                        "id": movie.get("id", "N/A"),
                        "title": movie.get("title", "UNKNOWN"),
                        "status": "failed",
                        "error": str(e),
                    }
                )
        return results
