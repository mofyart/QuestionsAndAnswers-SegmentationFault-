from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from app.models import Tag, Profile
from redis.exceptions import LockError

import time

CACHE_KEY_BEST_TAGS = 'best_tags'
CACHE_KEY_BEST_USERS = 'best_users'
CACHE_TIMEOUT = 60 * 2

LOCK_KEY_TAGS = 'lock_best_tags'
LOCK_KEY_USERS = 'lock_best_users'
LOCK_TIMEOUT = 60

def calculate_best_tags():
    return list(Tag.objects.best())

def calculate_best_users():
    return list(Profile.objects.best())

def refresh_cache_tags_users():
    tags = calculate_best_tags()
    users = calculate_best_users()

    cache.set(CACHE_KEY_BEST_TAGS, tags, CACHE_TIMEOUT)
    cache.set(CACHE_KEY_BEST_USERS, users, CACHE_TIMEOUT)

def get_cached_tags():
    data = cache.get(CACHE_KEY_BEST_TAGS)

    if data is not None:
        return data

    lock = cache.lock(LOCK_KEY_TAGS, timeout=LOCK_TIMEOUT)

    if lock.acquire(blocking=False):
        try:
            data = calculate_best_tags()
            cache.set(CACHE_KEY_BEST_TAGS, data, CACHE_TIMEOUT)
            return data
        finally:
            lock.release()

    time.sleep(0.5)
    return cache.get(CACHE_KEY_BEST_TAGS) or []

def get_cached_users():
    data = cache.get(CACHE_KEY_BEST_USERS)

    if data is not None:
        return data

    lock = cache.lock(LOCK_KEY_USERS, timeout=LOCK_TIMEOUT)

    if lock.acquire(blocking=False):
        try:
            data = calculate_best_users()
            cache.set(CACHE_KEY_BEST_USERS, data, CACHE_TIMEOUT)
            return data
        finally:
            lock.release()

    time.sleep(0.5)
    return cache.get(CACHE_KEY_BEST_USERS) or []
