import json


def setup_periodic_task():
    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    if not PeriodicTask.objects.filter(name="fetch_movies_task").exists():
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=6,
            period=IntervalSchedule.HOURS,
        )

        PeriodicTask.objects.create(
            interval=schedule,
            name="fetch_movie_task",
            task="movies.task.fetch_and_store_movies",
            args=json.dumps([]),
        )
