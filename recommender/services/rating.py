import pandas as pd

from recommender.models_.recommender_model import RecommederModel
from recommender.repositories.rating import RatingRepository


class RatingService:

    def __init__(self, repository: RatingRepository, model: RecommederModel):
        self.repo = repository
        self.model = model

    def rate_movie(self, user_id, movie_id, rating):
        """
        Validate and save rating for a giver user movie
        """
        if rating < 1 or rating > 100:
            raise ValueError("Rating must be between 1 and 100")
        success = self.repo.add_rating(user_id, movie_id, rating)
        if not success:
            raise RuntimeError(f"Rating insertion failed for user {user_id}")

    def get_recommendation(self, user_id, top_n=10):
        """
        Recommend to movies based on user's rating history using trained model
        """
        # 1. Get ratings
        ratings = self.repo.get_user_ratings(user_id)
        unrated_movies = self.repo.get_unrated_movies(user_id)

        if not ratings:
            return []

        formatted_ratings = [
            {
                "user_id": user_id,
                "movie_id": rating["movie_id"],
                "rating": rating["rating"],
            }
            for rating in ratings
        ]

        self.model.train(formatted_ratings)

        recommendations = []

        for movie in unrated_movies:
            movie_id = movie["tmdb_id"]
            score = self.model.predict(user_id, movie_id)
            movie["score"] = score
            recommendations.append(movie)

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_n]
