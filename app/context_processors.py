from .models import Tag, Profile

def get_best_tags(request):
    best_tags = Tag.objects.best()

    return {
        'best_tags' : best_tags
    }

def get_best_users(request):
    best_users = Profile.objects.best()

    return {
        'best_users' : best_users
    }
