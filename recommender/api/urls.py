from django.urls import path


from .views import RateMovieView, RecommendationMovieView

urlpatterns = [
    path("rate-movie/", RateMovieView.as_view(), name="rate"),
    path("recommend-movie/", RecommendationMovieView.as_view(), name="recommend"),
]
