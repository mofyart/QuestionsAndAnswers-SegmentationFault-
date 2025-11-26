from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class AnswerQuerySet(models.QuerySet):
    def add_likes(self):
        return self.annotate(likes_count=Count('likes'))

    def best(self):
        return self.add_likes().order_by('-likes_count')

class ManagerAnswer(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def best(self):
        return self.get_queryset().best()

class QuestionQuerySet(models.QuerySet):
    def add_likes(self):
        return self.annotate(likes_count=Count('likes'))

    def best(self):
        return self.add_likes().order_by('-likes_count')

    def new(self):
        return self.add_likes().order_by('-created_at')
class ManagerQuestion(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def add_likes(self):
        return self.get_queryset().add_likes()

    def best(self):
        return self.get_queryset().best()

    def new(self):
        return self.get_queryset().new()

class ManagerTag(models.Manager):
    def best(self):
        return self.annotate(count_questions=Count('questions')).order_by('-count_questions')[:9]
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    objects = ManagerTag()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True)

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "content_type", "object_id"], name="unique_like"),
        ]

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, related_name='questions')

    likes = GenericRelation(Like)

    objects = ManagerQuestion()

    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
class Answer(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False, blank=True, null=True)

    likes = GenericRelation(Like)

    objects = ManagerAnswer()

    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
