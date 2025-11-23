from .models import Tag

def get_best_tags(request):
    best_tags = Tag.objects.best()

    return {
        'best_tags' : best_tags
    }
