import json
import sys


from django.apps import AppConfig
from django.db.models.signals import post_migrate


from django_celery_beat.models import PeriodicTask, IntervalSchedule


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        if "test" in sys.argv:
            return

        # Avoid duplicate inserts
        def setup_periodic_task(sender, **kwargs):
            # create task if it does not exist
            if not PeriodicTask.objects.filter(name="fetch_movies_task").exists():
                schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=12,
                    period=IntervalSchedule.HOURS,
                )

                PeriodicTask.objects.create(
                    interval=schedule,
                    name="fetch_movies_task",
                    task="movies.tasks.fetch_and_store_movies",
                    args=json.dumps([]),
                )

        post_migrate.connect(setup_periodic_task, sender=self)
