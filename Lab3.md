# Лабораторная работа №3: Проектирование модели данных

## 📋 Описание

Реализовано проектирование модели базы данных для веб-приложения SegmentationFault. Создана полная архитектура данных с использованием Django ORM, включая связи между таблицами, custom manager'ы для оптимизации запросов и систему валидации данных.

**Цель:** Проектирование модели базы данных, наполнение её тестовыми данными и отображение этих данных на сайте.

---

## 1. 🗄️ Проектирование модели

### Описание реализации

Используя Django Models, спроектирована схема вашего приложения. Создана модель для основных сущностей: вопрос, ответ, тег, профиль пользователя и система лайков.

#### 1.1 Модель User (Пользователь)

Используется встроенная модель Django `django.contrib.auth.models.User` с дополнительной моделью `Profile` для расширения функционала.

```python
from django.contrib.auth.models import User

# Встроенные поля User:
# - username: уникальное имя пользователя
# - email: электронная почта
# - password: хэшированный пароль
# - first_name: имя
# - last_name: фамилия
# - is_active: активен ли пользователь
# - is_staff: имеет ли права администратора
# - is_superuser: суперпользователь ли
```

#### 1.2 Модель Profile (Профиль пользователя)

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    objects = ManagerProfile()
```

**Описание полей:**
- `user` - связь один-к-одному с User (при удалении пользователя удаляется и профиль)
- `nick_name` - уникальное прозвище пользователя (max 100 символов)
- `avatar` - изображение профиля пользователя (необязательное поле)

---

#### 1.3 Модель Tag (Тег)

```python
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    objects = ManagerTag()
```

**Описание:**
- Теги для категоризации вопросов
- `name` - уникальное имя тега (max 255 символов)

---

#### 1.4 Модель Question (Вопрос)

```python
class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                            related_name='user_questions')
    tags = models.ManyToManyField(Tag, related_name='questions')
    
    likes = GenericRelation(Like)
    
    objects = ManagerQuestion()
    
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    
    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})
```

**Описание полей:**
- `title` - название вопроса (max 255 символов)
- `text` - полный текст вопроса (TextField для больших текстов)
- `user` - автор вопроса (ForeignKey с PROTECT - нельзя удалить профиль если у него есть вопросы)
- `tags` - теги вопроса (ManyToMany отношение)
- `likes` - GenericRelation для связи с моделью Like
- `created_at` - дата создания (автоматически устанавливается при создании)
- `update_at` - дата последнего обновления (автоматически обновляется)

**Связи:**
- Один пользователь может создать много вопросов
- Один вопрос может иметь много тегов

---

#### 1.5 Модель Answer (Ответ)

```python
class Answer(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                            related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, 
                                related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False, blank=True, null=True)
    
    likes = GenericRelation(Like)
    
    objects = ManagerAnswer()
    
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
```

**Описание полей:**
- `user` - автор ответа (ForeignKey с PROTECT)
- `question` - вопрос, на который дан ответ (ForeignKey с CASCADE - при удалении вопроса удаляются все ответы)
- `text` - текст ответа (TextField)
- `is_correct` - отмечен ли ответ как правильный (по умолчанию False)
- `likes` - GenericRelation для связи с моделью Like
- `created_at` и `update_at` - даты создания и обновления

**Связи:**
- Один пользователь может написать много ответов
- Один вопрос может иметь много ответов
- При удалении вопроса удаляются все его ответы

---

#### 1.6 Модель Like (Лайк/Дизлайк) с GenericForeignKey

```python
class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    value = models.SmallIntegerField(default=1)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], 
                name="unique_like"
            ),
        ]
```

**Описание:**
- **GenericForeignKey** - позволяет связывать лайки с любой моделью (вопрос, ответ и т.д.)
- `user` - кто поставил лайк
- `content_type` - тип модели (Question или Answer)
- `object_id` - ID объекта (ID вопроса или ответа)
- `content_object` - автоматическая связь на объект
- `value` - значение лайка (1 для лайка, -1 для дизлайка)
- **UniqueConstraint** - ограничение на уровне БД, один пользователь может поставить только один лайк/дизлайк на один объект

**Преимущества GenericForeignKey:**
✅ Один лайк может быть как на вопрос, так и на ответ  
✅ Можно легко добавить лайки для других моделей (комментарии, статьи и т.д.)  
✅ Не нужно создавать отдельные таблицы для каждого типа лайка

---

### Диаграмма связей между моделями:

```
User (Django built-in)
  └─ Profile (OneToOne)
      ├─ Question (ForeignKey, related_name='user_questions')
      │   ├─ Tag (ManyToMany, related_name='questions')
      │   ├─ Answer (ForeignKey, related_name='answers')
      │   │   └─ Like (GenericForeignKey)
      │   └─ Like (GenericForeignKey)
      └─ Answer (ForeignKey, related_name='user_answers')
          └─ Like (GenericForeignKey)
      └─ Like (ForeignKey, related_name='likes')
```

---

## 2. 🔧 Manager и QuerySet методы

### Описание реализации

Реализованы custom Manager и QuerySet для оптимизации БД запросов и добавления функционала сортировки/фильтрации.

#### 2.1 QuestionQuerySet и ManagerQuestion

```python
class QuestionQuerySet(models.QuerySet):
    def add_likes(self):
        """Добавляет поле likes_count с суммой всех лайков"""
        return self.annotate(
            likes_count=Coalesce(Sum('likes__value'), Value(0))
        )
    
    def best(self):
        """Возвращает вопросы отсортированные по рейтингу (лучшие первыми)"""
        return self.add_likes().order_by('-likes_count')
    
    def new(self):
        """Возвращает вопросы отсортированные по дате создания (новые первыми)"""
        return self.add_likes().order_by('-created_at')
    
    def add_vote(self, user):
        """Добавляет информацию о голосе текущего пользователя"""
        if not user.is_authenticated:
            return self
        
        content_type = ContentType.objects.get_for_model(Question)
        
        vote_question = Like.objects.filter(
            content_type=content_type,
            object_id=OuterRef('pk'),
            user=user.profile
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
```

#### Использование в View:

```python
# Получить новые вопросы с количеством лайков и голосом текущего пользователя
all_questions = Question.objects.new().add_vote(request.user)

# Получить лучшие вопросы
hot_questions = Question.objects.best().prefetch_related('tags')

# Цепочка методов работает благодаря паттерну Manager
questions = Question.objects.new().add_likes().add_vote(request.user)
```

---

#### 2.2 AnswerQuerySet и ManagerAnswer

```python
class AnswerQuerySet(models.QuerySet):
    def add_likes(self):
        """Добавляет количество лайков"""
        return self.annotate(
            likes_count=Coalesce(Sum('likes__value'), Value(0))
        )
    
    def best(self):
        """Ответы отсортированы по рейтингу"""
        return self.add_likes().order_by('-likes_count')
    
    def new(self):
        """Ответы отсортированы по дате создания"""
        return self.add_likes().order_by('-created_at')
    
    def add_vote(self, user):
        """Добавляет информацию о голосе пользователя"""
        if not user.is_authenticated:
            return self
        
        content_type = ContentType.objects.get_for_model(Answer)
        
        vote_answer = Like.objects.filter(
            content_type=content_type,
            object_id=OuterRef('pk'),
            user=user.profile
        ).values('value')[:1]
        
        return self.annotate(user_vote=Subquery(vote_answer))
```

---

#### 2.3 ManagerTag

```python
class ManagerTag(models.Manager):
    def best(self):
        """Возвращает 9 самых популярных тегов"""
        return self.annotate(
            count_questions=Count('questions')
        ).order_by('-count_questions')[:9]
```

**Использование:** `Tag.objects.best()` - получить топ-9 тегов для сайдбара

---

#### 2.4 ManagerProfile

```python
class ManagerProfile(models.Manager):
    def best(self):
        """Возвращает 5 самых активных пользователей"""
        return self.annotate(
            count_questions=Count('user_questions', distinct=True)
        ).annotate(
            count_answers=Count('user_answers', distinct=True)
        ).annotate(
            count_activities=F('count_questions') + F('count_answers')
        ).order_by('-count_activities')[:5]
```

**Использование:** `Profile.objects.best()` - получить лучших участников для сайдбара

---

## 3. 📥 Наполнение данными

### Описание реализации

Создан Management Command для автоматического заполнения БД тестовыми данными.

#### Команда для запуска:

```bash
python manage.py fill_db [ratio]

# Примеры:
python manage.py fill_db 10    # Создать базовый объем данных
python manage.py fill_db 50    # Создать в 50 раз больше данных
python manage.py fill_db 100   # Создать в 100 раз больше данных
```

#### Файл: `app/management/commands/fill_db.py`

```python
import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    help = 'Fills the database with test data based on a given ratio.'
    
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=10, 
                          help='Multiplier for the amount of data.')
    
    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']
        
        # Базовые количества
        BASE_USERS = 10
        BASE_TAGS = 100
        BASE_QUESTIONS = 10
        BASE_ANSWERS = 10
        BASE_LIKES = 50
        
        # Итоговые количества
        total_users = BASE_USERS * ratio
        total_tags = BASE_TAGS * ratio
        total_questions = BASE_QUESTIONS * ratio
        total_answers = BASE_ANSWERS * ratio
        total_likes = BASE_LIKES * ratio
```

#### Этапы заполнения данных:

**1. Создание пользователей:**
```python
users_to_create = [
    User(
        username=faker.unique.user_name()[:150],
        email=faker.email(),
        password='password'
    ) for _ in range(total_users)
]
User.objects.bulk_create(users_to_create, batch_size=BATCH_SIZE)
```

**2. Создание профилей:**
```python
profiles_to_create = [
    Profile(
        user=user,
        nick_name=faker.unique.user_name()[:30],
        avatar=f'profile_pics/{random.randint(1, 5)}.jpg'
    ) for user in new_users
]
Profile.objects.bulk_create(profiles_to_create, batch_size=BATCH_SIZE)
```

**3. Создание тегов:**
```python
tags_to_create = [
    Tag(name=f'{faker.word()}_{i}_{random.randint(1, 10000)}') 
    for i in range(total_tags)
]
Tag.objects.bulk_create(tags_to_create, batch_size=BATCH_SIZE)
```

**4. Создание вопросов:**
```python
questions_to_create = []
for _ in range(total_questions):
    questions_to_create.append(Question(
        user_id=random.choice(profile_ids),
        title=faker.sentence(nb_words=5)[:250],
        text=faker.paragraph(nb_sentences=5)
    ))
    if len(questions_to_create) >= BATCH_SIZE:
        Question.objects.bulk_create(questions_to_create)
        questions_to_create = []
```

**5. Связывание вопросов и тегов:**
```python
for q_id in question_ids:
    chosen_tags = random.sample(tag_ids, k=random.randint(1, 3))
    for t_id in chosen_tags:
        QuestionTags(question_id=q_id, tag_id=t_id)
```

**6. Создание ответов:**
```python
answers_to_create = [
    Answer(
        user_id=random.choice(profile_ids),
        question_id=random.choice(question_ids),
        text=faker.paragraph(nb_sentences=3)
    ) for _ in range(total_answers)
]
Answer.objects.bulk_create(answers_to_create)
```

**7. Создание лайков:**
```python
for _ in range(total_likes):
    is_question = random.random() < 0.4  # 40% лайков на вопросы
    
    Like.objects.create(
        user_id=random.choice(profile_ids),
        content_type=question_content_type,
        object_id=random.choice(question_ids)
    )
```

---

## 4. 📊 Требования к объему данных

При использовании Management Command с коэффициентом заполнения создается следующий объем данных:

#### Базовый объем (ratio = 1):
- ✅ Пользователи: 10
- ✅ Вопросы: 10
- ✅ Ответы: 10
- ✅ Теги: 100
- ✅ Оценки пользователей: 50

#### При ratio = 10:
- ✅ Пользователи > 100
- ✅ Вопросы > 1 000
- ✅ Ответы > 10 000
- ✅ Теги > 1 000
- ✅ Оценки пользователей > 500 000

#### Команда для заполнения:

```bash
python manage.py fill_db [ratio]
```

**Пример:** Для создания 100K вопросов, 1M ответов и 2M лайков используйте:

```bash
python manage.py fill_db 10000
```

---

## 5. 🎯 Отображение данных

### Описание реализации

Разработаны views для отображения следующих страниц:

- **Список новых вопросов** (главная страница) - URL = `/`
- **Список "лучших" вопросов** - URL = `/hot/`
- **Список вопросов по тегу** - URL = `/tag/<tag_id>/`
- **Страница одного вопроса со списком ответов** - URL = `/question/<question_id>/`

Все views используют функцию пагинации, созданную на предыдущем занятии.

**Особенность:** В коде view не должно быть дублирующегося кода. Использовать функцию пагинации созданную на предыдущем занятии.

---

## 6. 🔐 Использование СУБД

### Описание реализации

По умолчанию Django использует **SQLite** - встраиваемую БД, которая представляет собой файл в каталоге с Django-проектом. Это решение удобно для отладки, но не может использоваться "в продакшене".

#### Требуется отказаться от SQLite в пользу иной реляционной СУБД на ваш выбор:

**Возможные варианты:**
- **MySQL** - широко распространенная СУБД
- **PostgreSQL** - мощная БД с расширенными возможностями

#### Конфигурация в `settings.py`:

**Для PostgreSQL:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'segmentationfault',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Для MySQL:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'segmentationfault',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### Установка необходимых пакетов:

**Для PostgreSQL:**
```bash
pip install psycopg2-binary
```

**Для MySQL:**
```bash
pip install mysqlclient
```

---

## 7. 📝 Валидация данных через Django Forms

### Описание реализации

Реализованы Django формы для валидации пользовательских данных перед сохранением в БД.

#### 7.1 LoginForm (Форма входа)

```python
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.lower() == 'admin':
            raise forms.ValidationError("Login with name 'admin' is prohibited.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_info = authenticate(username=username, password=password)
            if self.user_info is None:
                raise forms.ValidationError("Incorrect login or password.")
        
        return cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_info', None)
```

---

#### 7.2 RegisterForm (Форма регистрации)

```python
class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=100)
    email = forms.EmailField()
    nick_name = forms.CharField(min_length=4, max_length=100)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    repeat_password = forms.CharField(min_length=8, widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this login already exists")
        return username
    
    def clean_nick_name(self):
        nick_name = self.cleaned_data.get('nick_name')
        if Profile.objects.filter(nick_name=nick_name).exists():
            raise forms.ValidationError("User with this nick name already exists")
        return nick_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')
        
        if password != repeat_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
```

---

#### 7.3 QuestionForm (Форма создания вопроса)

```python
class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title")
    text = forms.CharField(required=False, label="Text")
    tags = forms.CharField(required=False, label="Tags")
    
    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags')
        
        if not tags_str:
            return []
        
        # Разбиваем теги по запятым и удаляем пробелы
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Удаляем дубликаты
        tags_list = list(set(tags_list))
        
        # Проверяем длину каждого тега
        for tag in tags_list:
            if len(tag) > 20:
                raise forms.ValidationError(f"Tag '{tag}' is too long (max 20 chars)")
        
        return tags_list
```

---

#### 7.4 AnswerForm (Форма ответа)

```python
class AnswerForm(forms.Form):
    text = forms.CharField(label="Text")
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        
        if len(text) < 10:
            raise forms.ValidationError("Your answer is too small (min 10 chars)")
        
        return text
```

---

## 📊 Итоговая таблица моделей

| Модель | Поля | Связи | Особенности |
|--------|------|-------|-------------|
| User | username, email, password | - | Django built-in |
| Profile | user, nick_name, avatar | OneToOne User | Custom manager |
| Tag | name | ManyToMany Question | Custom manager |
| Question | title, text, user, tags, created_at | FK Profile, M2M Tag, GenericRelation | Custom manager, QuerySet |
| Answer | text, user, question, is_correct | FK Profile, FK Question, GenericRelation | Custom manager, QuerySet |
| Like | user, content_type, object_id | FK Profile, GenericFK | Уникальность на БД уровне |

---

## ✨ Особенности реализации

✅ **GenericForeignKey** - система лайков работает для любых моделей  
✅ **QuerySet оптимизация** - использование `Subquery`, `Coalesce`, `annotate`  
✅ **Manager паттерн** - переиспользуемые методы фильтрации и сортировки  
✅ **Валидация форм** - проверка данных на уровне приложения  
✅ **Management Command** - автоматическое заполнение БД  
✅ **Bulk операции** - оптимизированное массовое создание объектов  
✅ **Внешняя СУБД** - использование PostgreSQL/MySQL вместо SQLite  
✅ **Защита от дубликатов** - UniqueConstraint в модели Like

---

## 🚀 Использованные технологии

- **ORM**: Django ORM с QuerySet и Manager
- **БД**: PostgreSQL/MySQL (вместо SQLite)
- **Генерация данных**: Faker library
- **Валидация**: Django Forms
- **Оптимизация**: prefetch_related, select_related, annotate, bulk_create

---

**Дата создания:** 17.04.2026  
**Разработчик:** Бусыгин А.Д. ИУ5-46Б
