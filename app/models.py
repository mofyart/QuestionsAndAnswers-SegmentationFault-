from django.db import models
from django.db.models import Count, F, Sum, Value
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db.models.functions import Coalesce
from django.db.models import OuterRef, Subquery

class AnswerQuerySet(models.QuerySet):
    def add_likes(self):
        return self.annotate(likes_count=Coalesce(Sum('likes__value'), Value(0)))

    def best(self):
        return self.add_likes().order_by('-likes_count')

    def new(self):
        return self.add_likes().order_by('-created_at')

    def add_vote(self, user):
        if not user.is_authenticated:
            return self

        content_type = ContentType.objects.get_for_model(Answer)

        vote_answer = Like.objects.filter(
            content_type = content_type,
            object_id = OuterRef('pk'),
            user = user.profile
        ).values('value')[:1]

        return self.annotate(user_vote=Subquery(vote_answer))



class ManagerAnswer(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def best(self):
        return self.get_queryset().best()

    def new(self):
        return self.get_queryset().new()

    def add_vote(self, user):
        return self.get_queryset().add_vote(user)

class QuestionQuerySet(models.QuerySet):
    def add_likes(self):
        return self.annotate(likes_count=Coalesce(Sum('likes__value'), Value(0)))

    def best(self):
        return self.add_likes().order_by('-likes_count')

    def new(self):
        return self.add_likes().order_by('-created_at')

    def add_vote(self, user):
        if not user.is_authenticated:
            return self

        content_type = ContentType.objects.get_for_model(Question)

        vote_question = Like.objects.filter(
            content_type = content_type,
            object_id = OuterRef('pk'),
            user = user.profile
        ).values('value')[:1]

        return self.annotate(user_vote=Subquery(vote_question))
class ManagerQuestion(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def add_likes(self):
        return self.get_queryset().add_likes()

    def best(self):
        return self.get_queryset().best()

    def new(self):
        return self.get_queryset().new()

    def add_vote(self, user):
        return self.get_queryset().add_vote(user)

class ManagerTag(models.Manager):
    def best(self):
        return self.annotate(count_questions=Count('questions')).order_by('-count_questions')[:9]

class ManagerProfile(models.Manager):
    def best(self):
        return self.annotate(
            count_questions=Count('user_questions', distinct=True)
        ).annotate(
            count_answers=Count('user_answers', distinct=True)
        ).annotate(
            count_activities=F('count_questions') + F('count_answers')
        ).order_by('-count_activities')[:5]


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    objects = ManagerTag()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    objects = ManagerProfile()
class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    value = models.SmallIntegerField(default=1)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "content_type", "object_id"], name="unique_like"),
        ]

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='user_questions')
    tags = models.ManyToManyField(Tag, related_name='questions')

    likes = GenericRelation(Like)

    objects = ManagerQuestion()

    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)

    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})
class Answer(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False, blank=True, null=True)

    likes = GenericRelation(Like)

    objects = ManagerAnswer()

    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
