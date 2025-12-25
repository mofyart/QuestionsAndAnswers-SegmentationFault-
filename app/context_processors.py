from .models import Tag, Profile
from .utils import get_centrifugo_token

# def get_best_tags(request):
#     best_tags = Tag.objects.best()

#     return {
#         'best_tags' : best_tags
#     }

# def get_best_users(request):
#     best_users = Profile.objects.best()

#     return {
#         'best_users' : best_users
#     }

def get_jwt_user(request):
    token = ""

    if request.user.is_authenticated:
        token = get_centrifugo_token(request.user.id)

    return {
        'centrifugo_token' : token
    }
