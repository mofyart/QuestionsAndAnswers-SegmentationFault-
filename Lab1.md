# Лабораторная работа №1: Верстка сайта SegmentationFault

## 📋 Описание

Реализована полная верстка веб-приложения SegmentationFault с использованием:
- **Фреймворк**: Django (шаблонизация)
- **Стилизация**: CSS с современным дизайном
- **Адаптивность**: Responsive design для мобильных устройств

---

## 1. 🎨 Верстка общего вида (Layout) страницы

### Описание реализации

Создана базовая верстка страницы в файле `base.html`, которая служит шаблоном для всех остальных страниц.

#### Основные компоненты:

**Заголовок (Header):**
- Логотип "SegmentationFault" с градиентом и стилизацией
- Поиск с выпадающим меню результатов
- Кнопка "ASK" для создания новых вопросов (видна только авторизованным пользователям)
- Профиль пользователя с аватаром и меню (логин/регистрация для гостей)

**Основной контент:**
- Макет в две колонки (3:1)
- Левая часть - список вопросов или контент страницы
- Правая часть (Sidebar) - популярные теги и лучшие участники

**Фоновый эффект:**
- Aurora-эффект с размытыми градиентными кругами

#### Примеры кода:

```html
<!-- Заголовок -->
<header>
    <div class="logo">
        <a href="{% url 'index' %}">SegmentationFault</a>
    </div>
    <div class="search">
        <input type="text" name="search" id="search-input"
               placeholder="Search" class="search-input">
        <div id="search-results" class="dropdown-menu"></div>
        {% if user.is_authenticated %}
            <a href="{% url 'ask' %}">
                <button class="search-button">ASK</button>
            </a>
        {% endif %}
    </div>
    <div class="profile">
        {% if user.is_authenticated %}
            <div class="profile-name">{{ user.profile.nick_name }}</div>
            <div class="avatar-box">
                <img src="{{ user.profile.avatar.url }}">
            </div>
            <div class="profile-info">
                <div class="profile-actions">
                    <a href="{% url 'settings' %}">settings</a>
                    <a href="{% url 'logout' %}">log out</a>
                </div>
            </div>
        {% endif %}
    </div>
</header>
```

```css
/* Стиль логотипа с градиентом */
.logo a {
    font-size: 3rem;
    font-weight: 800;
    background-image: linear-gradient(45deg, #3900f3, #9373ff, #ffffff);
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
}

/* Макет в две колонки */
.main-content {
    display: flex;
    gap: 2rem;
    padding: 2rem 0;
}

.questions-list {
    flex: 3; /* 75% ширины */
}

.sidebar {
    flex: 1; /* 25% ширины */
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Aurora эффект на фоне */
.background-aurora::before {
    background: linear-gradient(90deg, #5f9aff, #0022ff);
    filter: blur(150px);
    opacity: 0.3;
}
```

#### Особенности дизайна:
✅ Терпимые отступы (padding/margin) между блоками - `2rem`, `1.5rem`
✅ Темная тема с контрастными элементами
✅ Плавные переходы (transitions) при наведении
✅ Логотип в правой колонке слева
✅ Блоки в правой колонке (Popular Tags, Best Members)

---

## 2. 📝 Верстка списка вопросов на главной странице

### Описание реализации

Реализована страница `index.html`, которая наследует макет от `base.html` и выводит список всех вопросов с рейтингом, аватарками и тегами.

#### Структура вопроса:

Каждый вопрос представлен компонентом `question.html` с:
- Аватаром автора (слева)
- Рейтингом (кнопки лайков/дизлайков)
- Названием вопроса (ссылка на полную версию)
- Кратким описанием
- Тегами
- Ссылкой на ответы

#### Примеры кода:

```html
<!-- index.html -->
{% extends 'main/Layout/base.html' %}

{% block title %}Главная страница{% endblock %}

{% block content %}
    <div class="questions-list">
        {% include "main/Layout/header.html" with
            title="New Questions"
            link=linkHotQuestion
            linkName="Hot Questions" %}

        {% for question in questions %}
            {% include "main/Layout/question.html"
                with q=question tags=tags %}
        {% endfor %}

        {% include "main/Layout/paginator.html" %}
    </div>
{% endblock %}
```

```html
<!-- Layout/question.html (компонент) -->
<article class="question-full-item">
    <div class="question-meta">
        <!-- Аватар автора -->
        <div class="avatar-question">
            {% if q.user.avatar %}
                <img src="{{ q.user.avatar.url }}">
            {% else %}
                <img src="{% static 'main/default.jpg' %}">
            {% endif %}
        </div>

        <!-- Кнопки рейтинга (лайк/дизлайк) -->
        <div class="vote-controls">
            <button class="js-vote-btn upvote 
                    {% if q.user_vote == 1 %}active{% endif %}"
                    data-id="{{ q.id }}" data-type="question">
                <svg width="24" height="24">
                    <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
            </button>
            <div class="vote-count">{{ q.likes_count }}</div>
            <button class="js-vote-btn downvote">
                <svg width="24" height="24">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </button>
        </div>
    </div>

    <div class="question-details">
        <div class="question-title">
            <a href="{% url 'question' q.id %}">{{ q.title }}</a>
        </div>
        <p class="question-full-body">{{ q.text }}</p>
        <div class="question-footer">
            <div class="tags">
                Tags:
                {% for tag in q.tags.all %}
                    <a href="{% url 'tag' tag.id %}" class="tag">
                        {{ tag.name }}
                    </a>
                {% endfor %}
            </div>
        </div>
    </div>
</article>
```

```css
/* Стиль блока вопроса */
.question-full-item {
    background: rgba(30, 27, 46, 0.7);
    border: 1px solid #4A4A6A;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    gap: 1.5rem;
}

/* Аватар */
.avatar-question {
    width: 64px;
    height: 64px;
    flex-shrink: 0;
    border-radius: 8px;
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.avatar-question img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 6px;
}

/* Кнопки рейтинга */
.vote-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px;
    border-radius: 16px;
    width: fit-content;
}

.js-vote-btn {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.1);
    cursor: pointer;
    transition: all 0.2s ease;
}

.js-vote-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
    color: #ffffff;
}

.js-vote-btn.upvote.active {
    background-color: rgba(16, 185, 129, 0.2);
    color: #34d399;
}

/* Теги */
.tags a.tag {
    display: inline-block;
    background-color: #3a3a5a;
    color: #e0e0e0;
    padding: 4px 8px;
    border-radius: 5px;
    text-decoration: none;
    margin-left: 5px;
    transition: background-color 0.3s ease;
}

.tags a.tag:hover {
    background-color: #4a5de8;
}
```

#### Особенности дизайна:
✅ Аватарки авторов с border-radius
✅ Кнопки лайков с интерактивным дизайном
✅ Теги с разными цветами
✅ Ссылки на ответы
✅ Пагинатор внизу списка

---

## 3. 🔍 Верстка страницы одного вопроса

### Описание реализации

Страница `question.html` выводит полный вопрос и все ответы на него. Реализована с возможностью добавления новых ответов для авторизованных пользователей.

#### Основные элементы:

- Полный текст вопроса с рейтингом
- Список всех ответов на вопрос
- Форма для добавления нового ответа
- Пагинация для ответов
- Отображение ошибок валидации

#### Примеры кода:

```html
<!-- question.html -->
{% extends 'main/Layout/base.html' %}

{% block title %}Вопрос{% endblock %}

{% block content %}
    <div class="questions-list" data-question-id="{{ question.id }}">

        <!-- Блок ошибок -->
        {% if form.errors %}
            <div class="messages">
                {% for error in form.non_field_errors %}
                    <div class="alert-error">{{ error }}</div>
                {% endfor %}
                {% for field in form %}
                    {% for error in field.errors %}
                        <div class="alert-error">{{ error }}</div>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}

        <!-- Полный вопрос -->
        {% include 'main/Layout/question.html'
            with q=question tags=tags %}

        <!-- Все ответы -->
        <div class="answers-section">
            {% for answer in answers %}
                {% include 'main/Layout/answer.html'
                    with answer=answer %}
            {% endfor %}
        </div>

        <!-- Форма для добавления ответа -->
        {% if user.is_authenticated %}
            <form action="{% url 'question' question.id %}"
                  method="post" class="question-form">
                {% csrf_token %}
                {% include "main/Layout/formFilling.html"
                    with textareaPole=True
                         label="Your answer"
                         name="text"
                         rows="6"
                         placeholder="Enter your answer here.." %}
                {% include 'main/Layout/formAction.html'
                    with buttonBlock=True title="Answer" %}
            </form>
        {% endif %}

        <!-- Пагинация -->
        {% include "main/Layout/paginator.html" %}
    </div>
{% endblock %}
```

```html
<!-- Layout/answer.html -->
<article class="answer-item {% if answer.is_correct %} 
         correct-answer {% endif %}" id="answer-{{ answer.id }}">

    <div class="question-meta">
        <!-- Аватар автора ответа -->
        <div class="avatar-question">
            {% if answer.user.avatar %}
                <img src="{{ answer.user.avatar.url }}">
            {% else %}
                <img src="{% static 'main/default.jpg' %}">
            {% endif %}
        </div>

        <!-- Рейтинг ответа -->
        <div class="vote-controls">
            <button class="js-vote-btn upvote 
                    {% if answer.user_vote == 1 %}active{% endif %}"
                    data-id="{{ answer.id }}"
                    data-type="answer">
                <svg width="24" height="24">...</svg>
            </button>
            <div class="vote-count">{{ answer.likes_count }}</div>
            <button class="js-vote-btn downvote">
                <svg width="24" height="24">...</svg>
            </button>
        </div>
    </div>

    <div class="answer-details">
        <div class="answer-username">{{ answer.user.nick_name }}</div>
        <p>{{ answer.text }}</p>

        <!-- Чекбокс для отметки правильного ответа -->
        <div class="correct-marker">
            <input type="checkbox"
                   class="js-correct-btn"
                   id="correct-{{ answer.id }}"
                   data-answer-id="{{ answer.id }}"
                   {% if answer.is_correct %}checked{% endif %}
                   {% if request.user != question.user.user %}disabled{% endif %}>
            <label for="correct-{{ answer.id }}">Correct!</label>
        </div>
    </div>
</article>
```

```css
/* Блок с ошибками */
.alert-error {
    font-size: 1.4em;
    color: #ff5722;
}

/* Секция с ответами */
.answers-section {
    border-top: 1px solid #4A4A6A;
    padding-top: 1.5rem;
}

/* Стиль для правильного ответа */
.answer-item.correct-answer {
    background-color: rgba(0, 123, 255, 0.1);
    border-color: #007BFF;
}

/* Чекбокс для отметки правильного ответа */
.correct-marker {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.correct-marker input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #007BFF;
    cursor: pointer;
}
```

#### Особенности дизайна:
✅ Список тегов у вопроса
✅ Список ответов по верстке аналогичен листингу вопросов
✅ Пагинатор ответов
✅ Форма для добавления нового ответа (видна только авторизованным)

---

## 4. ✏️ Верстка формы добавления вопроса

### Описание реализации

Страница `ask.html` содержит форму для создания новых вопросов с валидацией и подсказками.

#### Поля формы:

1. **Title** - название вопроса (обычное текстовое поле)
2. **Text** - полное описание вопроса (textarea)
3. **Tags** - теги через запятую (с подсказкой)

#### Примеры кода:

```html
<!-- ask.html -->
{% extends 'main/Layout/base.html' %}

{% block title %}New Question{% endblock %}

{% block content %}
    <div class="content-column">
        {% include "main/Layout/header.html"
            with title="New Questions"
                 link=linkHotQuestion
                 linkName="Hot Questions" %}

        <!-- Блок ошибок -->
        {% if form.errors %}
            <div class="messages">
                {% for error in form.non_field_errors %}
                    <div class="alert-error">{{ error }}</div>
                {% endfor %}
                {% for field in form %}
                    {% for error in field.errors %}
                        <div class="alert-error">{{ error }}</div>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}

        <!-- Форма создания вопроса -->
        <form action="#" method="post" class="question-form">
            {% csrf_token %}

            <!-- Поле заголовка -->
            {% include "main/Layout/formFilling.html"
                with appointment="question-title"
                     label="Title"
                     name="title"
                     placeholder="Write text, please"
                     value=form.title.value %}

            <!-- Поле текста -->
            {% include "main/Layout/formFilling.html"
                with label="Text"
                     textareaPole=True
                     appointment="question-text"
                     name="text"
                     rows="8"
                     placeholder="Really, how ? Have no idea about it"
                     value=form.text.value %}

            <!-- Поле тегов -->
            {% include "main/Layout/formFilling.html"
                with appointment="question-tags"
                     label="Tags"
                     name="tags"
                     placeholder="moon, park, puzzle"
                     smallPole="True"
                     inscription="Specify the tags separated by commas"
                     value=form.tags.value %}

            <!-- Кнопка отправки -->
            {% include 'main/Layout/formAction.html'
                with buttonBlock=True title="Create" %}
        </form>
    </div>
{% endblock %}
```

```html
<!-- Layout/formFilling.html (переиспользуемый компонент) -->
<div class="form-group">
    <label for="{{ appointment }}">{{ label }}</label>

    {% if textareaPole %}
        <textarea
            id="{{ appointment }}"
            name="{{ name }}"
            rows="{{ rows }}"
            placeholder="{{ placeholder }}">{{ value|default:'' }}</textarea>
    {% else %}
        <input
            type="{{ type|default:'text' }}"
            id="{{ appointment }}"
            name="{{ name }}"
            placeholder="{{ placeholder }}"
            value="{{ value|default:'' }}">
    {% endif %}

    {% if smallPole %}
        <small>{{ inscription }}</small>
    {% endif %}
</div>
```

```css
/* Стиль формы */
.question-form .form-group {
    margin-bottom: 2rem;
}

.question-form label {
    display: block;
    font-size: 1.1rem;
    font-weight: 400;
    color: #e0e0e0;
    margin-bottom: 0.75rem;
}

/* Текстовые поля и textarea */
.question-form input[type="text"],
.question-form textarea {
    width: 100%;
    background-color: #1E1B2E;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    color: #FFFFFF;
    padding: 14px 18px;
    font-size: 1rem;
    font-family: 'Manrope', sans-serif;
    outline: none;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    box-sizing: border-box;
}

/* Placeholder текст */
.question-form input[type="text"]::placeholder,
.question-form textarea::placeholder {
    color: #8A8AA0;
}

/* Focus стиль */
.question-form input[type="text"]:focus,
.question-form textarea:focus {
    border-color: #7B68EE;
    box-shadow: 0 0 10px rgba(123, 104, 238, 0.2);
}

/* Textarea */
.question-form textarea {
    resize: vertical;
    min-height: 150px;
}

/* Подсказка для полей */
.question-form small {
    display: block;
    margin-top: 0.5rem;
    color: #8A8AA0;
    font-size: 0.9rem;
}

/* Кнопка отправки */
.submit-button {
    padding: 10px 30px;
    border: none;
    border-radius: 8px;
    background-color: #007BFF;
    color: white;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.submit-button:hover {
    background-color: #0056b3;
}
```

#### Особенности дизайна:
✅ Вывод сообщений об ошибках формы
✅ Подсказки к полям (для Tags поля)
✅ Ширина всех полей - 100%
✅ Max-width для textarea и текстовых полей
✅ Плавный переход цвета при фокусе

---

## 5. 🔐 Верстка форм логина и регистрации

### Описание реализации

Реализованы две страницы: `login.html` для входа и `register.html` для создания нового аккаунта.

#### Компоненты формы логина:

- Поле username
- Поле password
- Ссылка на регистрацию
- Кнопка "Log in"

#### Компоненты формы регистрации:

- Поле username
- Поле email
- Поле nick_name (никнейм)
- Поле password
- Поле repeat_password (повторение пароля)
- Выбор аватара (файл)
- Кнопка "Register"

#### Примеры кода:

```html
<!-- login.html -->
{% extends 'main/Layout/base.html' %}

{% block title %}Войти{% endblock %}

{% block content %}
    <div class="content-column">
        {% include "main/Layout/header.html" with title="Log In" %}

        <!-- Блок ошибок -->
        {% if form.errors %}
            <div class="messages">
                {% for error in form.non_field_errors %}
                    <div class="alert-error">{{ error }}</div>
                {% endfor %}
                {% for field in form %}
                    {% for error in field.errors %}
                        <div class="alert-error">{{ error }}</div>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}

        <div class="login-container">
            <form action="" method="post" class="login-form">
                {% csrf_token %}

                <!-- Username -->
                {% include "main/Layout/formFilling.html"
                    with appointment="login-username"
                         label="Log in"
                         name="username"
                         placeholder="Enter your login here"
                         value=form.username.value %}

                <!-- Password -->
                {% include "main/Layout/formFilling.html"
                    with appointment="login-password"
                         label="Password"
                         name="password"
                         placeholder="********"
                         type="password" %}

                <!-- Кнопка и ссылка на регистрацию -->
                {% url 'register' as registerUrl %}
                {% include "main/Layout/formAction.html"
                    with buttonBlock=True
                         title="Log in"
                         createAccountLink=registerUrl %}
            </form>
        </div>
    </div>
{% endblock %}
```

```html
<!-- register.html -->
{% extends 'main/Layout/base.html' %}

{% block title %}Регестрация{% endblock %}

{% block content %}
    <div class="content-column">
        {% include "main/Layout/header.html"
            with title="Registration" %}

        <!-- Блок ошибок -->
        {% if form.errors %}
            <div class="messages">
                {% for error in form.non_field_errors %}
                    <div class="alert-error">{{ error }}</div>
                {% endfor %}
                {% for field in form %}
                    {% for error in field.errors %}
                        <div class="alert-error">{{ error }}</div>
                    {% endfor %}
                {% endfor %}
            </div>
        {% endif %}

        <div class="login-container">
            <form action="" method="post" class="login-form"
                  enctype="multipart/form-data">
                {% csrf_token %}

                <!-- Username -->
                {% include 'main/Layout/formFilling.html'
                    with appointment="login-username"
                         label="Login"
                         name="username"
                         placeholder="Enter your login here"
                         value=form.username.value %}

                <!-- Email -->
                {% include 'main/Layout/formFilling.html'
                    with appointment="login-email"
                         label="Email"
                         name="email"
                         placeholder="Enter your Email here"
                         value=form.email.value %}

                <!-- Nickname -->
                {% include 'main/Layout/formFilling.html'
                    with appointment="login-nickname"
                         label="NickName"
                         name="nick_name"
                         placeholder="Enter your nickname here"
                         value=form.nick_name.value %}

                <!-- Password -->
                {% include 'main/Layout/formFilling.html'
                    with appointment="login-password"
                         label="Password"
                         name="password"
                         placeholder="********"
                         type="password" %}

                <!-- Repeat Password -->
                {% include 'main/Layout/formFilling.html'
                    with appointment="login-password"
                         label="Repeat Password"
                         name="repeat_password"
                         placeholder="********"
                         type="password" %}

                <!-- Avatar Upload -->
                {% include 'main/Layout/formAction.html'
                    with avatarChoose=True
                         label="Avatar"
                         button="Choose"
                         name="avatar" %}

                <!-- Register Button -->
                {% include 'main/Layout/formAction.html'
                    with buttonBlock=True title="Register" %}
            </form>
        </div>
    </div>
{% endblock %}
```

```html
<!-- Layout/formAction.html -->
<div class="form-actions">
    <!-- Кнопка отправки -->
    {% if buttonBlock %}
        <button type="submit" class="submit-button">
            {{ title }}
        </button>
    {% endif %}

    <!-- Ссылка на регистрацию (для логина) -->
    {% if createAccountLink %}
        <a href="{{ createAccountLink }}" class="create-account-link">
            create new account
        </a>
    {% endif %}

    <!-- Выбор аватара (для регистрации) -->
    {% if avatarChoose %}
        <div class="avatar-upload-container">
            <label for="login-password" class="avatar-label">
                {{ label }}
            </label>

            <label for="avatar_input" class="file-choose-button">
                {{ button }}
            </label>

            <span id="file-name" class="file-name-text">
                No file chosen
            </span>

            <input type="file"
                   id="avatar_input"
                   name="avatar"
                   class="file-input-hidden"
                   onchange="document.getElementById('file-name')
                            .textContent = this.files[0].name">
        </div>
    {% endif %}
</div>
```

```css
/* Контейнер логина/регистрации */
.login-container {
    max-width: 500px;
}

.login-container h1 {
    margin: 0 0 1rem 0;
    font-size: 2.8rem;
    color: #ffffff;
    font-weight: 800;
}

/* Блок с ошибками */
.error-message {
    color: #ff4d4d;
    font-size: 1.1rem;
    margin-bottom: 2rem;
    background-color: rgba(255, 77, 77, 0.1);
    border: 1px solid rgba(255, 77, 77, 0.3);
    padding: 10px 15px;
    border-radius: 8px;
}

/* Групповые элементы формы */
.login-form .form-group {
    margin-bottom: 1.5rem;
}

.login-form label {
    display: block;
    font-size: 1.1rem;
    color: #ffffff;
    margin-bottom: 0.75rem;
}

/* Поля ввода */
.login-form input[type="text"],
.login-form input[type="password"] {
    width: 100%;
    background-color: #1E1B2E;
    border: 1px solid #4A4A6A;
    border-radius: 8px;
    color: #FFFFFF;
    padding: 14px 18px;
    font-size: 1rem;
    font-family: 'Manrope', sans-serif;
    outline: none;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    box-sizing: border-box;
}

/* Focus стиль */
.login-form input[type="text"]:focus,
.login-form input[type="password"]:focus {
    border-color: #7B68EE;
    box-shadow: 0 0 10px rgba(123, 104, 238, 0.2);
}

/* Контейнер для выбора файла */
.avatar-upload-container {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

/* Лейбл для аватара */
.avatar-label {
    color: white;
    font-size: 1rem;
    margin: 0;
}

/* Кнопка выбора файла */
.file-choose-button {
    background-color: #5220f5;
    color: white;
    padding: 8px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    display: inline-block;
    transition: background-color 0.3s ease;
}

.file-choose-button:hover {
    background-color: #331cc4;
}

/* Текст имени файла */
.file-name-text {
    color: #f0f0f1;
    font-size: 1.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

/* Скрытое поле ввода файла */
.file-input-hidden {
    display: none;
}

/* Форма-контейнер */
.form-actions {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-top: 0.5rem;
    margin-bottom: 1em;
}

/* Кнопка "Log in" / "Register" */
.submit-button {
    padding: 10px 30px;
    border: none;
    border-radius: 8px;
    background-color: #007BFF;
    color: white;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.submit-button:hover {
    background-color: #0056b3;
}

/* Ссылка на регистрацию -->
.create-account-link {
    color: #007BFF;
    text-decoration: none;
    font-weight: 700;
}

.create-account-link:hover {
    text-decoration: underline;
}
```

#### Особенности дизайна:
✅ Вывод сообщений об ошибках формы и подсказок
✅ Ширина полей ввода - 100%
✅ Max-width контейнера формы - 500px
✅ Выбор аватара с отображением имени файла
✅ Ссылка на создание нового аккаунта в форме логина
✅ Плавные переходы при фокусе на полях

---

## 📊 Итоговая статистика

| Компонент | Статус |
|-----------|--------|
| Base layout | ✅ Реализовано |
| Header с меню | ✅ Реализовано |
| Sidebar с тегами и участниками | ✅ Реализовано |
| Список вопросов | ✅ Реализовано |
| Рейтинг (лайки/дизлайки) | ✅ Реализовано |
| Страница вопроса и ответы | ✅ Реализовано |
| Форма создания вопроса | ✅ Реализовано |
| Формы логина и регистрации | ✅ Реализовано |
| CSS стилизация | ✅ Реализовано |
| Адаптивность | ✅ Реализовано |
| Пагинация | ✅ Реализовано |
| Поиск | ✅ Реализовано |

---

## 🎯 Использованные технологии

- **Backend**: Django 4.x (шаблонизация)
- **Frontend**: HTML5, CSS3
- **Стилизация**: Custom CSS с поддержкой flex/grid
- **Фонт**: Google Fonts (Manrope)
- **Цветовая схема**: Темная тема (Dark Mode)
- **Иконки**: SVG инлайн

---

## ✨ Особенности дизайна

1. **Modern Dark Theme** - Темная тема с контрастными элементами
2. **Gradient Effects** - Использование градиентов для логотипа и кнопок
3. **Smooth Transitions** - Плавные переходы при наведении
4. **Responsive Design** - Адаптивная верстка для мобильных устройств
5. **Aurora Background** - Красивый фоновый эффект с размытыми кругами
6. **Consistent Spacing** - Единообразные отступы между элементами

---

**Дата создания:** 17.04.2026
**Разработчик:** Бксыгин А.Д. ИУ5-46Б
