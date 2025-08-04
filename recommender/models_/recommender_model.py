from surprise import Dataset, Reader, SVD
import pandas as pd


class RecommederModel:

    def __init__(self):
        self.model = None
        self.trained = False

    def train(self, ratings):
        if not ratings:
            raise ValueError("No rating data provided for training")

        df = pd.DataFrame(ratings)

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)
        training_set = data.build_full_trainset()

        self.model = SVD()
        self.model.fit(training_set)
        self.trained = True

    def predict(self, user_id, movie_id):
        if not self.trained:
            raise ValueError("Model is nt trained")
        prediction = self.model.predict(uid=user_id, iid=movie_id)
        return prediction.est
