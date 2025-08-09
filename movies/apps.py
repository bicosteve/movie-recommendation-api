from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "movies"

    def ready(self):
        import json
        import sys

        if "test" in sys.argv or "makemigrations" in sys.argv or "migrate" in sys.argv:
            return

        from django.db.models.signals import post_migrate
        from .initializers import setup_periodic_task

        post_migrate.connect(
            lambda **kwargs: setup_periodic_task(),
            sender=self,
        )
