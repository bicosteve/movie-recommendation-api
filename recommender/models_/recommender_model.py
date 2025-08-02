from surprise import Dataset, Reader, SVD


class RecommederModel:
    def __init__(self, data_frame):
        self.data_frame = data_frame
        self.model = None

    def train(self):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            self.data_frame[["user_id", "movie_id", "rating"]], reader
        )
        training_set = data.build_full_trainset()
        self.model = SVD()
        self.model.fit(training_set)

    def predict(self, user_id, movie_id):
        return self.model.predict(uid=user_id, iid=movie_id).est
