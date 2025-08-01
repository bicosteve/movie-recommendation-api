from movies.repo.movies import MovieRepository


class MovieService:
    def __init__(self):
        self.movie_repo = MovieRepository()

    def insert_movies(self, movies):
        results = self.movie_repo.add_movies(movies)
        total = len(results)
        successes = [r for r in results if r["status"] == "success"]
        failures = [r for r in results if r["status"] == "failed"]
        return {
            "total": total,
            "inserted": len(successes),
            "failed": len(failures),
            "successes": successes,
            "failures": failures,
        }
