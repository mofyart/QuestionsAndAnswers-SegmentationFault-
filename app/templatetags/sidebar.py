from django import template
from app.services import get_cached_tags, get_cached_users

register = template.Library()

@register.simple_tag
def show_best_tags():
    return get_cached_tags()

@register.simple_tag
def show_best_users():
    return get_cached_users()
