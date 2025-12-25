from django.apps import AppConfig
import sys
import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        is_runserver = 'runserver' in sys.argv[0]
        is_gunicorn = 'gunicorn' in sys.argv[0]

        if is_runserver or is_gunicorn:
            try:
                from .tasks import refresh_best_tags_users

                print("GOOOOOOOOOOOOOOOOOOOOOOOD")
                refresh_best_tags_users.delay()
            except Exception as e:
                print(f"Warning: Could not send warmup task: {e}")
