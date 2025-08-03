import pandas as pd

from recommender.models_.recommender_model import RecommederModel
from recommender.repositories.rating import RatingRepository


class RatingService:

    def __init__(self, repository, model):
        self.repo = repository
        self.model = model

    def rate_movie(self, user_id, movie_id, rating):
        if rating < 1 or rating > 100:
            raise ValueError("Rating must be between 1 and 100")
        success = self.repo.add_rating(user_id, movie_id, rating)
        if not success:
            raise RuntimeError(f"Rating insertion failed for user {user_id}")

    def get_recommendation(self, user_id, top_n=10):
        # 1. Get ratings
        ratings = self.repo.get_all_ratings(user_id)
        unrated_movies = self.repo.get_unrated_movies(user_id)

        if not ratings:
            return []

        self.model.train(ratings)

        recommendations = []

        for movie in unrated_movies:
            score = self.model.predict(user_id, movie["imdb_id"])
            movie["score"] = score

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:10]
