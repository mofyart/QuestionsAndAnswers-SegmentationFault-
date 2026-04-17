# Лабораторная работа №2: Обработка HTTP запросов

## 📋 Описание

Реализована полная обработка HTTP запросов веб-приложения SegmentationFault с использованием Django фреймворка. Приложение обрабатывает запросы всех основных страниц, управляет маршрутизацией URL, реализует пагинацию и AJAX функционал.

---

## 🔧 1. Создание директории проекта ask_pupkin

### Описание реализации

Создана корневая директория проекта с правильной структурой папок и файлов для Django приложения.

#### Структура директории:

```
SegmentationFault/
├── SegmentationFault/      # Корневая папка проекта
│   ├── settings.py         # Конфигурация Django
│   ├── urls.py             # Маршруты основного проекта
│   ├── wsgi.py             # WSGI конфигурация
│   └── asgi.py             # ASGI конфигурация
├── app/                     # Основное приложение
│   ├── migrations/          # Миграции БД
│   ├── static/              # Статические файлы (CSS, JS, картинки)
│   │   └── main/
│   │       ├── css/
│   │       ├── js/
│   │       └── img/
│   ├── templates/           # HTML шаблоны
│   │   └── main/
│   │       ├── Layout/
│   │       ├── index.html
│   │       ├── login.html
│   │       └── ...
│   ├── uploads/             # Загруженные файлы пользователей
│   ├── models.py            # Модели БД
│   ├── views.py             # Views для обработки запросов
│   ├── urls.py              # Маршруты приложения
│   ├── forms.py             # Django формы
│   └── admin.py             # Конфигурация админ-панели
├── manage.py                # Утилита управления Django
└── requirements.txt         # Зависимости проекта
```

#### Команды для создания структуры:

```bash
# Создание корневой папки проекта
mkdir -p ~/projects/ask_pupkin
cd ~/projects/ask_pupkin

# Создание папок для статики и шаблонов
mkdir -p {static,uploads,templates}
mkdir -p static/{css,js,img}

# Создание Django проекта
django-admin startproject ask_pupkin .
python manage.py startapp app
```

---

## 🎯 2. Создание Django проекта и приложения

### Описание реализации

Инициализирован Django проект "SegmentationFault" с приложением "app". Все необходимые компоненты (модели, формы, views) интегрированы в приложение.

#### Основные файлы:

```python
# settings.py - основная конфигурация
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',  # Наше приложение
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'app', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

# Базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'segmentationfault',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📨 3. Отображение данных (Views)

### Описание реализации

Реализовано 8 основных views функций для обработки различных типов HTTP запросов.

#### 3.1 Главная страница (index)

**Назначение:** Отображение списка всех новых вопросов

**HTTP метод:** GET  
**URL:** `/`  
**Шаблон:** `index.html`

```python
def index(request):
    """
    Отображение списка новых вопросов на главной странице
    """
    # Получаем все вопросы, отсортированные по дате (новые первыми)
    all_questions = Question.objects.new().prefetch_related('tags').add_vote(request.user)
    
    # Пагинируем результаты
    page = paginate(request, all_questions)
    
    return render(request, 'index.html', context={
        'questions': page.object_list,  # Вопросы на текущей странице
        'page_obj': page,               # Объект пагинатора
        'tags': Tag.objects.all(),      # Все теги для сайдбара
    })
```

**Особенности:**
- Использует querySet с методом `new()` для сортировки по дате
- Применяет `prefetch_related` для оптимизации БД запросов
- Использует `add_vote()` для добавления информации о голосах текущего пользователя
- Пагинирует результаты по 5 вопросов на странице

---

#### 3.2 Список "горячих" вопросов (hotQuestion)

**Назначение:** Отображение самых рейтинговых вопросов

**HTTP метод:** GET  
**URL:** `/hotquestion/`  
**Шаблон:** `hotquestion.html`

```python
def hotQuestion(request):
    """
    Отображение самых популярных вопросов по рейтингу
    """
    # Получаем вопросы отсортированные по рейтингу (лучшие первыми)
    hot_questions = Question.objects.best().prefetch_related('tags').add_vote(request.user)
    
    page = paginate(request, hot_questions)
    
    return render(request, 'hotquestion.html', context={
        'questions': page.object_list,
        'page_obj': page,
    })
```

---

#### 3.3 Страница одного вопроса (newAnswer)

**Назначение:** Отображение вопроса, всех его ответов и формы для добавления нового ответа

**HTTP метод:** GET (отображение), POST (добавление ответа)  
**URL:** `/question/<int:question_id>`  
**Шаблон:** `question.html`

```python
def newAnswer(request, question_id):
    """
    Обработка страницы вопроса и добавление новых ответов
    """
    question = get_object_or_404(Question, pk=question_id)
    
    # Обработка POST запроса (добавление нового ответа)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Создаем новый ответ
            answer = Answer.objects.create(
                text=data['text'],
                user=request.user.profile,
                question=question
            )
            
            # Отправляем уведомление через WebSocket (Centrifugo)
            answer_html = render_to_string('main/Layout/answer.html',
                                         {'answer': answer},
                                         request=request)
            
            try:
                client = Client(CENTRIFUGO_API_URL, api_key=CENTRIFUGO_API_KEY)
                client.publish(PublishRequest(
                    channel=f"question:{question_id}",
                    data={'html': answer_html}
                ))
            except Exception as err:
                print(f"Centrifugo error: {err}")
            
            # Перенаправляем на страницу вопроса с якорем на новый ответ
            url = reverse('question', args=[question.pk])
            return redirect(f"{url}?page={1}#answer-{answer.id}")
    else:
        form = AnswerForm()
    
    # Получение всех ответов на вопрос
    query_set = Question.objects.add_likes().add_vote(request.user)
    question_for_render = get_object_or_404(query_set, pk=question_id)
    
    answers = question_for_render.answers.new().add_vote(request.user)
    
    # Пагинация ответов
    page = paginate(request, answers)
    
    return render(request, 'question.html', context={
        'form': form,
        'answers': page.object_list,
        'page_obj': page,
        'question': question_for_render,
        'tags': question_for_render.tags.all()
    })
```

---

#### 3.4 Вопросы по тегу (readTag)

**Назначение:** Отображение всех вопросов с определенным тегом

**HTTP метод:** GET  
**URL:** `/tag/<int:tag_id>`  
**Шаблон:** `tag.html`

```python
def readTag(request, tag_id):
    """
    Отображение всех вопросов с определённым тегом
    """
    tag = get_object_or_404(Tag, pk=tag_id)
    
    # Получаем все вопросы с этим тегом, отсортированные по лучшим
    questions_tag = tag.questions.best().prefetch_related('tags')
    
    page = paginate(request, questions_tag)
    
    return render(request, 'tag.html', context={
        'questions': page.object_list,
        'page_obj': page,
        'tag_title': tag.name,
    })
```

---

#### 3.5 Форма создания нового вопроса (newQuestion)

**Назначение:** Отображение и обработка формы создания вопроса

**HTTP метод:** GET (отображение), POST (создание вопроса)  
**URL:** `/ask/`  
**Шаблон:** `ask.html`

```python
def newQuestion(request):
    """
    Обработка формы создания нового вопроса
    """
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Создаем вопрос
            question = Question.objects.create(
                title=data['title'],
                text=data['text'],
                user=request.user.profile,
            )
            
            # Обрабатываем теги
            tags_list = data['tags']  # Список тегов из формы
            
            for tag in tags_list:
                # Получаем или создаем тег
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                question.tags.add(tag_obj)
            
            # Перенаправляем на новый вопрос
            return redirect(question)
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})
```

---

#### 3.6 Форма логина (logIn)

**Назначение:** Аутентификация пользователя

**HTTP метод:** GET (отображение), POST (проверка учетных данных)  
**URL:** `/login/`  
**Шаблон:** `login.html`

```python
def logIn(request):
    """
    Обработка формы входа пользователя
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            if user:
                login(request, user)  # Сохраняем сессию
                return redirect('index')  # Перенаправляем на главную
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})
```

---

#### 3.7 Форма регистрации (registrate)

**Назначение:** Создание нового пользователя

**HTTP метод:** GET (отображение), POST (создание пользователя)  
**URL:** `/register/`  
**Шаблон:** `register.html`

```python
def registrate(request):
    """
    Обработка формы регистрации нового пользователя
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Создаем пользователя Django
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            # Создаем профиль пользователя
            profile = Profile.objects.create(
                user=user,
                nick_name=data['nick_name']
            )
            
            # Добавляем аватар если загружен
            if data['avatar']:
                profile.avatar = data['avatar']
                profile.save()
            
            # Логируем пользователя
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})
```

---

#### 3.8 Выход из аккаунта (logOut)

**Назначение:** Завершение сессии пользователя

**HTTP метод:** GET  
**URL:** `/logout/`

```python
def logOut(request):
    """
    Выход пользователя из системы
    """
    logout(request)  # Удаляем сессию
    return redirect('index')  # Перенаправляем на главную
```

---

#### 3.9 Страница настроек (readSettings)

**Назначение:** Изменение профиля пользователя

**HTTP метод:** GET (отображение), POST (сохранение изменений)  
**URL:** `/settings/`  
**Шаблон:** `settings.html`

```python
def readSettings(request):
    """
    Отображение и обработка формы настроек профиля
    """
    user = request.user
    
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Обновляем данные пользователя Django
            if data['username']:
                user.username = data['username']
            if data['email']:
                user.email = data['email']
            user.save()
            
            # Обновляем профиль
            if data['nick_name']:
                user.profile.nick_name = data['nick_name']
            if data['avatar']:
                user.profile.avatar = data['avatar']
            user.profile.save()
            
            return redirect('settings')
    else:
        # Заполняем форму текущими значениями
        initial_data = {
            'username': user.username,
            'email': user.email,
            'nick_name': user.profile.nick_name,
        }
        form = SettingsForm(initial=initial_data)
    
    return render(request, 'settings.html', {'form': form})
```

---

## 🌐 4. Маршрутизация URL

### Описание реализации

Реализована система маршрутизации для всех страниц и API endpoints приложения.

#### Файл: `app/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы (GET запросы)
    path('', views.index, name="index"),
    path('ask/', views.newQuestion, name="ask"),
    path('question/<int:question_id>', views.newAnswer, name="question"),
    path('tag/<int:tag_id>', views.readTag, name="tag"),
    path('settings/', views.readSettings, name="settings"),
    path('login/', views.logIn, name="login"),
    path('register/', views.registrate, name="register"),
    path('hotquestion/', views.hotQuestion, name="hotquestion"),
    path('logout/', views.logOut, name="logout"),
    
    # AJAX endpoints (POST запросы)
    path('ajax/vote/', views.updateLike, name="object_like"),
    path('ajax/correct/', views.updateCorrect, name="object_correct"),
    path('ajax/search/', views.searchItem, name="search_object")
]
```

#### Таблица маршрутов:

| URL | Метод | View | Описание |
|-----|-------|------|---------|
| `/` | GET | `index` | Список новых вопросов |
| `/ask/` | GET/POST | `newQuestion` | Форма создания вопроса |
| `/question/<id>` | GET/POST | `newAnswer` | Страница вопроса и ответы |
| `/tag/<id>` | GET | `readTag` | Вопросы по тегу |
| `/settings/` | GET/POST | `readSettings` | Настройки профиля |
| `/login/` | GET/POST | `logIn` | Форма входа |
| `/register/` | GET/POST | `registrate` | Форма регистрации |
| `/hotquestion/` | GET | `hotQuestion` | Рейтинговые вопросы |
| `/logout/` | GET | `logOut` | Выход из системы |
| `/ajax/vote/` | POST | `updateLike` | API для лайков/дизлайков |
| `/ajax/correct/` | POST | `updateCorrect` | API для отметки правильного ответа |
| `/ajax/search/` | GET | `searchItem` | API для поиска |

---

## 🔄 5. Функция пагинации

### Описание реализации

Реализована переиспользуемая функция пагинации для всех списков объектов.

```python
def paginate(request, objects, per_page=5):
    """
    Функция для пагинации списка объектов
    
    Args:
        request: HTTP запрос (содержит параметр page)
        objects: QuerySet объектов для пагинации
        per_page: Количество объектов на странице (по умолчанию 5)
    
    Returns:
        Page: Объект страницы с методами для получения объектов и навигации
    """
    # Получаем номер страницы из GET параметра
    page_num = request.GET.get('page', 1)
    
    # Создаем пагинатор
    paginator = Paginator(objects, per_page)
    
    try:
        # Пытаемся получить запрошенную страницу
        page = paginator.page(page_num)
    except PageNotAnInteger:
        # Если номер страницы не число, переходим на первую
        page = paginator.page(1)
    except EmptyPage:
        # Если запрошена несуществующая страница, переходим на последнюю
        page = paginator.page(paginator.num_pages)
    
    return page
```

#### Использование в шаблонах:

```html
<!-- Список объектов на текущей странице -->
{% for question in page.object_list %}
    <div class="question-item">{{ question.title }}</div>
{% endfor %}

<!-- Пагинатор -->
{% include "main/Layout/paginator.html" %}
```

#### Объект Page содержит:

```python
page.object_list      # Список объектов на текущей странице
page.number           # Номер текущей страницы
page.paginator        # Объект пагинатора
page.has_previous()   # Есть ли предыдущая страница
page.has_next()       # Есть ли следующая страница
page.previous_page_number()  # Номер предыдущей страницы
page.next_page_number()      # Номер следующей страницы
```

---

## 💻 6. AJAX обработчики (API Endpoints)

### 6.1 Обработка лайков/дизлайков (updateLike)

**HTTP метод:** POST  
**URL:** `/ajax/vote/`  
**Требует авторизацию:** Да

```python
@require_POST
@login_required
def updateLike(request):
    """
    AJAX обработчик для добавления/удаления лайков и дизлайков
    
    Expected JSON:
    {
        "object_id": 1,
        "object_type": "question" или "answer",
        "action": "like" или "dislike"
    }
    """
    try:
        # Парсим JSON из тела запроса
        data = json.loads(request.body)
        object_id = data.get('object_id')
        object_type = data.get('object_type')
        action = data.get('action')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Маппируем тип объекта на модель
    model_map = {
        'question': Question,
        'answer': Answer
    }
    
    Model = model_map.get(object_type)
    
    if not Model:
        return JsonResponse({'error': 'Wrong object type'}, status=400)
    
    user = request.user.profile
    obj = get_object_or_404(Model, pk=object_id)
    
    # Получаем ContentType для модели
    content_type = ContentType.objects.get_for_model(obj)
    
    # Проверяем существующий лайк/дизлайк
    existing_like = Like.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.id,
    ).first()
    
    # Определяем новое значение (+1 для лайка, -1 для дизлайка)
    new_value = 1 if action == 'like' else -1
    
    # Логика обновления:
    # - Если уже есть такой же лайк/дизлайк - удаляем (toggle)
    # - Если есть противоположный - обновляем на новый
    # - Если нет - создаем новый
    if existing_like:
        if existing_like.value == new_value:
            existing_like.delete()  # Удаляем если тот же
        else:
            existing_like.value = new_value  # Меняем на противоположный
            existing_like.save()
    else:
        Like.objects.create(
            content_type=content_type,
            user=user,
            object_id=obj.id,
            value=new_value
        )
    
    # Возвращаем новый рейтинг
    new_rating = obj.likes.aggregate(total=Sum('value'))['total'] or 0
    return JsonResponse({'rating': new_rating})
```

#### Пример JavaScript вызова:

```javascript
// Отправка AJAX запроса для лайка
fetch('/ajax/vote/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        object_id: 42,
        object_type: 'question',
        action: 'like'
    })
})
.then(response => response.json())
.then(data => {
    console.log('New rating:', data.rating);
});
```

---

### 6.2 Обработка отметки правильного ответа (updateCorrect)

**HTTP метод:** POST  
**URL:** `/ajax/correct/`  
**Требует авторизацию:** Да (только автор вопроса)

```python
@require_POST
@login_required
def updateCorrect(request):
    """
    AJAX обработчик для отметки ответа как правильного/неправильного
    
    Expected JSON:
    {
        "answer_id": 5,
        "is_correct": true или false
    }
    """
    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        is_correct = data.get('is_correct')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Wrong object type'}, status=400)
    
    answer = get_object_or_404(Answer, pk=answer_id)
    question = answer.question
    
    # Проверяем что текущий пользователь - автор вопроса
    if question.user.user != request.user:
        return JsonResponse({'error': 'No permission'}, status=403)
    
    # Обновляем статус правильного ответа
    answer.is_correct = is_correct
    answer.save()
    
    return JsonResponse({'status': 'ok'}, status=200)
```

---

### 6.3 Поиск (searchItem)

**HTTP метод:** GET  
**URL:** `/ajax/search/`

```python
def searchItem(request):
    """
    AJAX поиск вопросов с полнотекстовым поиском и fallback на LIKE
    
    Query params:
        q: строка для поиска (минимум 2 символа)
    
    Returns JSON:
    {
        "results": [
            {"id": 1, "title": "..."},
            ...
        ]
    }
    """
    query = request.GET.get('q')
    
    # Не выполняем поиск если запрос менее 2 символов
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Полнотекстовый поиск PostgreSQL
    search_vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
    search_query = SearchQuery(query)
    
    # Результаты с высоким рейтингом релевантности
    full_find_objects = Question.objects.annotate(
        rank=SearchRank(search_vector, search_query)
    ).filter(rank__gte=0.1)
    
    # Fallback поиск через LIKE
    similar_find_objects = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    )
    
    # Объединяем результаты, убираем дубликаты и берем топ 5
    list_objects = (full_find_objects | similar_find_objects).distinct().order_by('-id')[:5]
    
    # Формируем JSON ответ
    data = [
        {
            'id': q.id,
            'title': q.title,
        } for q in list_objects
    ]
    
    return JsonResponse({'results': data})
```

---

## 📊 Итоговая таблица HTTP обработчиков

| Endpoint | Метод | Авторизация | Функция | Описание |
|----------|-------|-------------|---------|---------|
| `/` | GET | - | `index` | Список вопросов |
| `/ask/` | GET/POST | POST | `newQuestion` | Создание вопроса |
| `/question/<id>` | GET/POST | POST | `newAnswer` | Вопрос и ответы |
| `/tag/<id>` | GET | - | `readTag` | Вопросы по тегу |
| `/hotquestion/` | GET | - | `hotQuestion` | Рейтинговые вопросы |
| `/login/` | GET/POST | - | `logIn` | Вход |
| `/register/` | GET/POST | - | `registrate` | Регистрация |
| `/settings/` | GET/POST | ✓ | `readSettings` | Профиль |
| `/logout/` | GET | ✓ | `logOut` | Выход |
| `/ajax/vote/` | POST | ✓ | `updateLike` | Лайки/дизлайки |
| `/ajax/correct/` | POST | ✓ | `updateCorrect` | Отметка ответа |
| `/ajax/search/` | GET | - | `searchItem` | Поиск |

---

## 🔐 Защита запросов

### Декораторы использованные в проекте:

```python
# Требует POST метод
@require_POST
def updateLike(request):
    ...

# Требует авторизацию
@login_required
def readSettings(request):
    ...

# Комбинированное использование
@require_POST
@login_required
def updateCorrect(request):
    ...
```

---

## ✨ Особенности реализации

✅ **Полнотекстовый поиск** - использование PostgreSQL SearchVector  
✅ **QuerySet оптимизация** - prefetch_related для снижения БД запросов  
✅ **AJAX интеграция** - асинхронные запросы без перезагрузки  
✅ **WebSocket поддержка** - real-time обновления через Centrifugo  
✅ **Валидация форм** - использование Django Forms  
✅ **Ограничение доступа** - проверка прав доступа и авторизации  
✅ **Обработка ошибок** - JsonResponse с соответствующими статусами  
✅ **Пагинация** - удобная навигация по большим спискам

---

**Дата создания:** 17.04.2026  
**Разработчик:** Бусыгин А.Д. ИУ5-46Б
