import pandas as pd

from recommender.models_.recommender_model import RecommederModel
from recommender.repositories.rating import RatingRepository


class RatingService:

    def __init__(self):
        self.rating_repo = RatingRepository()

    def insert_rating(self, user_id, movie_id, rating):
        self.rating_repo.add_rating(user_id, movie_id, rating)

    def make_recommendation(self, user_id, top_n=10):
        # 1. Get ratings
        ratings = self.rating_repo.get_all_ratings(user_id)

        if not ratings:
            return []

        df = pd.DataFrame(ratings)

        # 2. Train the model
        model = RecommederModel(df)
        model.train()

        # 3. Get unrated movies

        # 4. Predict & Sort
