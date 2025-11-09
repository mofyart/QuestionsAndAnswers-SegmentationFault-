from django.contrib import admin

from app.models import Tag, Like, Answer, Question, Profile

admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Profile)
