import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommender.settings")

app = Celery("movie_recommender")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
