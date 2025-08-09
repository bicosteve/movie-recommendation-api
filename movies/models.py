from django.db import models


# Create your models here.
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)
    genres = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=False, blank=False)
    poster_url = models.URLField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movies"
