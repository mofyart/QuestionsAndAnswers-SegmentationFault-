# Лабораторная работа №4: Авторизация и обработка форм

## 📋 Описание

Реализована полная система авторизации и аутентификации пользователей с использованием встроенной системы Django. Разработаны и интегрированы основные формы добавления данных с валидацией, обработкой ошибок и защитой от CSRF атак.

**Цель:** Подключение встроенной системы авторизации Django и разработка основных форм добавления данных.

---

## 1. 🔐 Авторизация и регистрация пользователей

### Описание реализации

Используется встроенная в Django система пользователей (`django.contrib.auth`), которая имеет готовые методы для логина и регистрации.

#### Основные функции Django auth:

```python
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

# Аутентификация пользователя
user = authenticate(request=None, username=username, password=password)

# Вход пользователя в систему
login(request, user)

# Выход пользователя
logout(request)

# Создание нового пользователя
user = User.objects.create_user(
    username='john',
    email='john@example.com',
    password='secure_password'
)

# Проверка авторизации
if request.user.is_authenticated:
    # Пользователь авторизован
    pass
```

#### Преимущества встроенной системы:
✅ Хеширование паролей (PBKDF2, bcrypt, Argon2)  
✅ Управление сессиями  
✅ Защита от основных уязвимостей  
✅ Встроенные декораторы для ограничения доступа  
✅ Интеграция с админ-панелью Django

---

## 2. 📝 Необходимые формы авторизации

### 2.1 Форма логина (LoginForm)

**URL:** `/login/`  
**Метод:** GET (отображение), POST (проверка учетных данных)  
**Доступна:** Всем пользователям

#### Структура формы:

```python
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Запрещаем вход под именем 'admin'
        if username.lower() == 'admin':
            raise forms.ValidationError("Login with name 'admin' is prohibited.")
        
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Проверяем учетные данные
            self.user_info = authenticate(
                request=None, 
                username=username, 
                password=password
            )
            
            if self.user_info is None:
                raise forms.ValidationError("Incorrect login or password.")
            
            if not self.user_info.is_active:
                raise forms.ValidationError("User is not active")
        
        return cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_info', None)
```

#### View для обработки логина:

```python
def logIn(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            if user:
                # Сохраняем сессию пользователя
                login(request, user)
                
                # Получаем URL для редиректа из параметра continue
                next_url = request.GET.get('continue', 'index')
                return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})
```

#### HTML шаблон:

```html
<form action="" method="post" class="login-form">
    {% csrf_token %}
    
    {% include "main/Layout/formFilling.html" 
        with appointment="login-username" 
             label="Log in" 
             name="username" 
             placeholder="Enter your login here" 
             value=form.username.value %}
    
    {% include "main/Layout/formFilling.html" 
        with appointment="login-password" 
             label="Password" 
             name="password" 
             placeholder="********" 
             type="password" %}
    
    {% if form.errors %}
        {% for error in form.non_field_errors %}
            <div class="alert-error">{{ error }}</div>
        {% endfor %}
    {% endif %}
    
    <button type="submit" class="submit-button">Log in</button>
    <a href="{% url 'register' %}" class="create-account-link">
        create new account
    </a>
</form>
```

#### Особенности:
✅ Параметр `continue` для редиректа после входа  
✅ Сохранение введенных данных при ошибке  
✅ Защита от перебора паролей  
✅ Проверка активности пользователя

---

### 2.2 Форма регистрации (RegisterForm)

**URL:** `/register/`  
**Метод:** GET (отображение), POST (создание пользователя)  
**Доступна:** Всем пользователям

#### Структура формы:

```python
class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=100, label="Username")
    email = forms.EmailField(label="Email")
    nick_name = forms.CharField(min_length=4, max_length=100, label="NickName")
    password = forms.CharField(
        min_length=8, 
        widget=forms.PasswordInput, 
        label="Password"
    )
    repeat_password = forms.CharField(
        min_length=8, 
        widget=forms.PasswordInput, 
        label="Repeat Password"
    )
    avatar = forms.ImageField(required=False, label="Avatar")
    
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
        
        if password is None:
            raise forms.ValidationError("Incorrect password")
        
        if repeat_password is None:
            raise forms.ValidationError("Incorrect repeating password")
        
        if password != repeat_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
```

#### View для обработки регистрации:

```python
def registrate(request):
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
            
            # Создаем профиль с дополнительными данными
            profile = Profile.objects.create(
                user=user,
                nick_name=data['nick_name']
            )
            
            # Добавляем аватар если загружен
            if data['avatar']:
                profile.avatar = data['avatar']
                profile.save()
            
            # Логируем пользователя сразу после регистрации
            login(request, user)
            
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})
```

#### Требования:
✅ Пользователь вводит все необходимые поля  
✅ Email, username и nick_name должны быть уникальными  
✅ Пароль минимум 8 символов  
✅ Пароли должны совпадать  
✅ Аватар необязателен  
✅ После успешной регистрации пользователь авторизуется

---

### 2.3 Ссылка "Выход" (Logout)

**URL:** `/logout/`  
**Метод:** GET  
**Доступна:** Только авторизованным пользователям

#### View для выхода:

```python
def logOut(request):
    logout(request)
    return redirect('index')
```

#### HTML в шаблоне:

```html
{% if user.is_authenticated %}
    <a href="{% url 'logout' %}">log out</a>
{% else %}
    <a href="{% url 'login' %}">log in</a>
{% endif %}
```

---

### 2.4 Форма редактирования профиля (SettingsForm)

**URL:** `/settings/`  
**Метод:** GET (отображение), POST (обновление)  
**Доступна:** Только авторизованным пользователям

#### Структура формы:

```python
class SettingsForm(forms.Form):
    username = forms.CharField(required=False, max_length=100, label="Username")
    email = forms.EmailField(required=False, label="Email")
    nick_name = forms.CharField(required=False, max_length=100, label="NickName")
    avatar = forms.ImageField(required=False, label="Avatar")
    
    def __init__(self, *args, **kwargs):
        # Получаем текущего пользователя
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if username.lower() == 'admin':
            raise forms.ValidationError("Login with name 'admin' is prohibited.")
        
        # Проверяем уникальность для других пользователей
        if User.objects.filter(username=username).exclude(
            pk=self.user.pk
        ).exists():
            raise forms.ValidationError("User with this login already exists")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exclude(
            pk=self.user.pk
        ).exists():
            raise forms.ValidationError("User with this email already exists")
        
        return email
    
    def clean_nick_name(self):
        nick_name = self.cleaned_data.get('nick_name')
        
        if Profile.objects.filter(nick_name=nick_name).exclude(
            user=self.user
        ).exists():
            raise forms.ValidationError("User with this nick name already exists")
        
        return nick_name
```

#### View для обработки профиля:

```python
@login_required
def readSettings(request):
    user = request.user
    
    if request.method == 'POST':
        form = SettingsForm(
            request.POST, 
            request.FILES, 
            user=request.user
        )
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Обновляем данные Django User
            if data['username']:
                user.username = data['username']
            if data['email']:
                user.email = data['email']
            user.save()
            
            # Обновляем Profile
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
        form = SettingsForm(initial=initial_data, user=user)
    
    return render(request, 'settings.html', {'form': form})
```

#### Особенности:
✅ Доступна только авторизованным пользователям (@login_required)  
✅ Все поля опциональные  
✅ Проверка уникальности исключает текущего пользователя  
✅ Поля заполнены текущими значениями

---

## 3. 📤 Необходимые формы добавления данных

### 3.1 Форма добавления вопроса (QuestionForm)

**URL:** `/ask/`  
**Метод:** GET (отображение), POST (создание вопроса)  
**Доступна:** Только авторизованным пользователям

#### Структура формы:

```python
class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title")
    text = forms.CharField(required=False, label="Text")
    tags = forms.CharField(required=False, label="Tags")
    
    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags')
        
        if not tags_str:
            return []
        
        # Разбиваем по запятым и удаляем пробелы
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Удаляем дубликаты
        tags_list = list(set(tags_list))
        
        # Проверяем длину каждого тега
        for tag in tags_list:
            if len(tag) > 20:
                raise forms.ValidationError(
                    f"Tag '{tag}' is too long (max 20 chars)"
                )
        
        return tags_list
```

#### View для обработки:

```python
@login_required
def newQuestion(request):
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
            tags_list = data['tags']
            for tag in tags_list:
                # Получаем или создаем тег
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                question.tags.add(tag_obj)
            
            # Перенаправляем на созданный вопрос
            return redirect(question)
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})
```

#### HTML шаблон:

```html
<form action="#" method="post" class="question-form">
    {% csrf_token %}
    
    <!-- Название вопроса -->
    {% include "main/Layout/formFilling.html" 
        with appointment="question-title" 
             label="Title" 
             name="title" 
             placeholder="Write text, please" 
             value=form.title.value %}
    
    <!-- Текст вопроса -->
    {% include "main/Layout/formFilling.html" 
        with label="Text" 
             textareaPole=True 
             appointment="question-text" 
             name="text" 
             rows="8" 
             placeholder="Really, how? Have no idea about it" 
             value=form.text.value %}
    
    <!-- Теги -->
    {% include "main/Layout/formFilling.html" 
        with appointment="question-tags" 
             label="Tags" 
             name="tags" 
             placeholder="moon, park, puzzle" 
             smallPole="True" 
             inscription="Specify the tags separated by commas" 
             value=form.tags.value %}
    
    <!-- Ошибки валидации -->
    {% if form.errors %}
        <div class="messages">
            {% for field in form %}
                {% for error in field.errors %}
                    <div class="alert-error">{{ error }}</div>
                {% endfor %}
            {% endfor %}
        </div>
    {% endif %}
    
    <button type="submit" class="submit-button">Create</button>
</form>
```

#### Требования:
✅ Название вопроса обязательно  
✅ Теги опциональны, но если указаны - разделены запятыми  
✅ Каждый тег не более 20 символов  
✅ Удаляются дубликаты тегов  
✅ Доступна только авторизованным пользователям

---

### 3.2 Форма добавления ответа (AnswerForm)

**URL:** `/question/<id>/`  
**Метод:** POST (создание ответа)  
**Доступна:** Только авторизованным пользователям

#### Структура формы:

```python
class AnswerForm(forms.Form):
    text = forms.CharField(label="Text")
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        
        if len(text) < 10:
            raise forms.ValidationError(
                "Your answer is too small (min 10 chars)"
            )
        
        return text
```

#### View для обработки:

```python
@login_required
def newAnswer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Создаем ответ
            answer = Answer.objects.create(
                text=data['text'],
                user=request.user.profile,
                question=question
            )
            
            # Перенаправляем на страницу вопроса с якорем на ответ
            url = reverse('question', args=[question.pk])
            return redirect(f"{url}?page={1}#answer-{answer.id}")
    else:
        form = AnswerForm()
    
    # Получаем ответы для страницы
    answers = question.answers.new().add_vote(request.user)
    page = paginate(request, answers)
    
    return render(request, 'question.html', context={
        'form': form,
        'answers': page.object_list,
        'page_obj': page,
        'question': question,
    })
```

#### HTML шаблон:

```html
<form action="{% url 'question' question.id %}" method="post" 
      class="question-form">
    {% csrf_token %}
    
    {% include "main/Layout/formFilling.html" 
        with textareaPole=True 
             label="Your answer" 
             name="text" 
             rows="6" 
             placeholder="Enter your answer here.." 
             value=form.text.value %}
    
    {% if form.errors %}
        <div class="messages">
            {% for error in form.non_field_errors %}
                <div class="alert-error">{{ error }}</div>
            {% endfor %}
        </div>
    {% endif %}
    
    <button type="submit" class="submit-button">Answer</button>
</form>
```

#### Требования:
✅ Минимум 10 символов в ответе  
✅ Доступна только на странице вопроса  
✅ Доступна только авторизованным пользователям  
✅ После успеха - редирект на страницу вопроса с якорем на новый ответ

---

## 4. ✅ Требования предъявляемые к формам

### 4.1 Валидация и сообщения об ошибках

```html
<!-- Вывод сообщений об ошибках -->
{% if form.errors %}
    <div class="messages">
        <!-- Общие ошибки формы -->
        {% for error in form.non_field_errors %}
            <div class="alert-error">{{ error }}</div>
        {% endfor %}
        
        <!-- Ошибки отдельных полей -->
        {% for field in form %}
            {% for error in field.errors %}
                <div class="alert-error">{{ error }}</div>
            {% endfor %}
        {% endfor %}
    </div>
{% endif %}
```

**Особенности:**
✅ Все ошибки выводятся пользователю  
✅ Ошибки видны в красном цвете (#ff5722)  
✅ Сообщения понятны пользователю

---

### 4.2 Сохранение данных при ошибке

```html
<!-- Значения автоматически восстанавливаются -->
<input type="text" 
       name="username" 
       value="{{ form.username.value }}">

<textarea name="text">{{ form.text.value }}</textarea>
```

**Django автоматически сохраняет:**
✅ Введенные значения в `form.field_name.value`  
✅ Состояние формы при ошибке валидации  
✅ Пользователю не нужно заново вводить данные

---

### 4.3 Метод POST для отправки форм

```html
<form action="" method="post" class="question-form">
    {% csrf_token %}
    
    <!-- Поля формы -->
    
    <button type="submit">Submit</button>
</form>
```

**Требования:**
✅ Все формы используют метод POST  
✅ GET используется только для чтения данных  
✅ Защита от повторного отправления при обновлении страницы

---

### 4.4 Редирект после успешной обработки

```python
if form.is_valid():
    # Обрабатываем данные
    obj = Model.objects.create(...)
    
    # Перенаправляем на новую страницу
    return redirect('page_name')
```

**Преимущества:**
✅ Предотвращает повторное отправление (POST-Redirect-GET паттерн)  
✅ Пользователь видит результат обработки  
✅ История браузера остается чистой

---

### 4.5 Защита от CSRF

```html
<form method="post">
    {% csrf_token %}
    <!-- Поля формы -->
</form>
```

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF защита
]

# views.py
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def my_view(request):
    pass
```

**CSRF токен:**
✅ Автоматически добавляется Django в каждую форму  
✅ Проверяется при POST запросах  
✅ Защита от несанкционированных действий от имени пользователя

---

### 4.6 Использование django.forms

```python
from django import forms

class MyForm(forms.Form):
    # Декларативное определение полей
    field_name = forms.CharField(max_length=100)
    
    # Валидация на уровне поля
    def clean_field_name(self):
        value = self.cleaned_data.get('field_name')
        if some_condition:
            raise forms.ValidationError("Error message")
        return value
    
    # Валидация на уровне формы
    def clean(self):
        cleaned_data = super().clean()
        # Проверки между полями
        return cleaned_data
```

**Преимущества django.forms:**
✅ Автоматическая генерация HTML  
✅ Встроенная валидация  
✅ CSRF защита  
✅ Обработка разных типов данных  
✅ Кастомизация через виджеты

---

## 📊 Итоговая таблица форм

| Форма | URL | Метод | Авторизация | Назначение |
|-------|-----|-------|-------------|-----------|
| LoginForm | `/login/` | GET/POST | - | Вход пользователя |
| RegisterForm | `/register/` | GET/POST | - | Регистрация |
| SettingsForm | `/settings/` | GET/POST | ✓ | Редактирование профиля |
| QuestionForm | `/ask/` | GET/POST | ✓ | Создание вопроса |
| AnswerForm | `/question/<id>/` | POST | ✓ | Ответ на вопрос |

---

## 🔒 Декораторы и защита

### login_required декоратор

```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    # Эта view доступна только авторизованным пользователям
    # Неавторизованные перенаправляются на /login/
    pass
```

### require_POST декоратор

```python
from django.views.decorators.http import require_POST

@require_POST
def api_endpoint(request):
    # Эта view принимает только POST запросы
    pass
```

### Комбинированная защита

```python
@require_POST
@login_required
def protected_post_view(request):
    # Принимает только POST запросы от авторизованных пользователей
    pass
```

---

## 💡 Работа с сессиями

### Установка сессии при логине

```python
from django.contrib.auth import login

def logIn(request):
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)  # Сохраняет сессию
        return redirect('home')
```

### Проверка авторизации в шаблоне

```html
{% if user.is_authenticated %}
    <p>Привет, {{ user.profile.nick_name }}!</p>
    <a href="{% url 'logout' %}">Выход</a>
{% else %}
    <a href="{% url 'login' %}">Вход</a>
    <a href="{% url 'register' %}">Регистрация</a>
{% endif %}
```

### Проверка авторизации в view

```python
def my_view(request):
    if request.user.is_authenticated:
        # Пользователь авторизован
        profile = request.user.profile
    else:
        # Пользователь не авторизован
        return redirect('login')
```

---

## ✨ Особенности реализации

✅ **Встроенная безопасность** - Django обеспечивает хеширование паролей  
✅ **CSRF защита** - автоматическая во всех формах  
✅ **Управление сессиями** - встроенное в Django  
✅ **Валидация на уровне поля и формы** - гибкая система проверок  
✅ **Сохранение данных при ошибке** - удобство пользователя  
✅ **POST-Redirect-GET паттерн** - предотвращение дублирования  
✅ **Декораторы доступа** - @login_required, @require_POST  
✅ **Расширяемость** - легко добавлять новые формы и валидацию

---

## 🚀 Использованные технологии

- **Аутентификация**: Django contrib.auth
- **Формы**: Django Forms с валидацией
- **Сессии**: Django Session Framework
- **Безопасность**: CSRF Protection, Password Hashing (PBKDF2)
- **Декораторы**: login_required, require_POST
- **Редирект**: Django redirect() с named URLs

---

## 📝 Шпаргалка по часто используемому коду

### Проверка авторизации

```python
if request.user.is_authenticated:
    # Авторизован
    pass
```

### Получение профиля пользователя

```python
profile = request.user.profile
nick_name = profile.nick_name
avatar = profile.avatar
```

### Создание объекта, связанного с пользователем

```python
Question.objects.create(
    user=request.user.profile,
    title=title,
    text=text
)
```

### Валидация уникальности поля

```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError("Email already exists")
    return email
```

### Вывод ошибок в шаблоне

```html
{% if form.errors %}
    {% for error in form.non_field_errors %}
        <div class="error">{{ error }}</div>
    {% endfor %}
{% endif %}
```

---

**Дата создания:** 17.04.2026  
**Разработчик:** Бусыгин А.Д. ИУ5-46Б
