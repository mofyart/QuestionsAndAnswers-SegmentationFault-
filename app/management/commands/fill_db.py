import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from app.models import Profile, Tag, Question, Answer, Like


BASE_USERS = 10
BASE_TAGS = 100
BASE_QUESTIONS = 10
BASE_ANSWERS = 10
BASE_LIKES = 2000
BATCH_SIZE = 10


class Command(BaseCommand):
    help = 'Fills the database with test data based on a given ratio.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=100, help='Multiplier for the amount of data. Default is 100.')

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(f"Starting to fill the database with ratio x{ratio}")

        self.stdout.write("Deleting old generated data")
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        Tag.objects.all().delete()

        faker = Faker()
        faker.unique.clear()

        total_users = BASE_USERS * ratio
        total_tags = BASE_TAGS * ratio
        total_questions = BASE_QUESTIONS * ratio
        total_answers = BASE_ANSWERS * ratio
        total_likes = BASE_LIKES * ratio

        self.stdout.write(f"Creating {total_users} users and profiles")
        users_to_create = [User(username=faker.unique.user_name(), email=faker.email(), password='password') for _ in range(total_users)]

        new_users = User.objects.bulk_create(users_to_create, BATCH_SIZE)

        # --- ИЗМЕНЕНИЯ ЗДЕСЬ ---
        # Добавляем nickname и avatar.
        # Предполагаем, что у тебя есть 5 картинок: 1.jpg, 2.jpg ... 5.jpg
        profiles_to_create = [
            Profile(
                user=user,
                nickname=faker.user_name(),  # Генерируем никнейм
                avatar=f'profile_pics/{random.randint(1, 5)}.jpg'  # Выбираем случайную картинку
            ) for user in new_users
        ]
        # -----------------------

        _ = Profile.objects.bulk_create(profiles_to_create, BATCH_SIZE)

        profile_ids = list(Profile.objects.values_list('id', flat=True))

        self.stdout.write(f"Creating {total_tags} tags")
        tags_to_create = [Tag(name=f'tag_{i}') for i in range(total_tags)]
        _ = Tag.objects.bulk_create(tags_to_create, BATCH_SIZE)
        tag_ids = list(Tag.objects.values_list('id', flat=True))

        self.stdout.write(f"Creating {total_questions} questions")
        questions_to_create = []
        for _ in range(total_questions):
            questions_to_create.append(Question(
                user_id=random.choice(profile_ids),
                title=faker.sentence(nb_words=5),
                text=faker.paragraph(nb_sentences=5)
            ))
            if len(questions_to_create) >= BATCH_SIZE:
                _ = Question.objects.bulk_create(questions_to_create)
                questions_to_create = []
        if questions_to_create:
            _ = Question.objects.bulk_create(questions_to_create)
        question_ids = list(Question.objects.values_list('id', flat=True))

        self.stdout.write("Linking tags to questions")
        QuestionTags = Question.tags.through
        question_tags_to_create = []
        for q_id in question_ids:
            for _ in range(random.randint(1, 3)):
                question_tags_to_create.append(
                    QuestionTags(question_id=q_id, tag_id=random.choice(tag_ids))
                )
            if len(question_tags_to_create) >= BATCH_SIZE:
                _ = QuestionTags.objects.bulk_create(question_tags_to_create, ignore_conflicts=True)
                question_tags_to_create = []
        if question_tags_to_create:
            _ = QuestionTags.objects.bulk_create(question_tags_to_create, ignore_conflicts=True)

        self.stdout.write(f"Creating {total_answers} answers")
        answers_to_create = []
        for _ in range(total_answers):
            answers_to_create.append(Answer(
                user_id=random.choice(profile_ids),
                question_id=random.choice(question_ids),
                text=faker.paragraph(nb_sentences=3)
            ))
            if len(answers_to_create) >= BATCH_SIZE:
                _ = Answer.objects.bulk_create(answers_to_create)
                answers_to_create = []
        if answers_to_create:
            _ = Answer.objects.bulk_create(answers_to_create)
        answer_ids = list(Answer.objects.values_list('id', flat=True))

        self.stdout.write(f"Creating {total_likes} likes")
        question_content_type = ContentType.objects.get_for_model(Question)
        answer_content_type = ContentType.objects.get_for_model(Answer)
        likes_to_create = []

        for _ in range(total_likes):
            content_type, object_id = (question_content_type, random.choice(question_ids)) if random.random() < 0.4 else (answer_content_type, random.choice(answer_ids))
            likes_to_create.append(Like(
                user_id=random.choice(profile_ids),
                content_type=content_type,
                object_id=object_id
            ))
            if len(likes_to_create) >= BATCH_SIZE:
                _ = Like.objects.bulk_create(likes_to_create, ignore_conflicts=True)
                likes_to_create = []
        if likes_to_create:
            _ = Like.objects.bulk_create(likes_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Database has been filled successfully!'))
