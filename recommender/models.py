from django.db import models
from django.conf import settings
from movies.models import Movie


# Create your models here.
class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, to_field="tmdb_id", on_delete=models.CASCADE)
    rating = models.FloatField()

    class Meta:
        unique_together = ("user", "movie")
