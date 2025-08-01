from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        import json
        import sys
        from django.db.models.signals import post_migrate

        if "test" in sys.argv:
            return

        # Avoid duplicate inserts
        def setup_periodic_task(sender, **kwargs):
            from django_celery_beat.models import PeriodicTask, IntervalSchedule

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
