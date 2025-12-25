from celery import shared_task
from app.services import refresh_cache_tags_users

@shared_task
def refresh_best_tags_users():
    refresh_cache_tags_users()
