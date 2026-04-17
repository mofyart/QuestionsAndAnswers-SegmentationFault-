# Лабораторная работа №5: Загрузка картинок и обработка AJAX запросов

## 📋 Описание

Реализована функциональность загрузки изображений (аватаров) пользователями и обработка асинхронных AJAX запросов для взаимодействия с вопросами и ответами без перезагрузки страницы.

**Цель:** Добавление функционала аватарок (загрузка картинок) и обработка AJAX запросов (лайки, отметка правильного ответа).

---

## 1. 📸 Загрузка картинок

### Описание реализации

Для хранения картинок используются встроенные инструменты Django: `django.db.models.ImageField` для хранения URL картинки в модели и `django.forms.ImageField` для описания поля в форме.

#### 1.1 Конфигурация Django

В файле `settings.py` необходимо настроить пути для загруженных файлов:

```python
# settings.py

import os

# Директория для загруженных файлов
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL для доступа к загруженным файлам
MEDIA_URL = '/media/'

# Для локальной разработки в urlpatterns добавить:
# path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT})
```

#### 1.2 Конфигурация для Nginx (продакшен)

```nginx
# nginx.conf
location /media {
    alias /path/to/project/media;
}
```

---

### 1.3 Модель с ImageField

```python
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=100, unique=True)
    
    # ImageField для хранения аватара
    avatar = models.ImageField(
        upload_to='profile_pics',  # Сохраняется в media/profile_pics/
        null=True,                  # Может быть пустым
        blank=True                  # Опциональное поле
    )
```

**Параметры ImageField:**
- `upload_to` - поддиректория для сохранения файлов
- `null=True` - может быть NULL в БД
- `blank=True` - опциональное поле в формах

---

### 1.4 Форма с ImageField

```python
from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    nick_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    
    # ImageField для загрузки аватара
    avatar = forms.ImageField(
        required=False,             # Опциональное поле
        label="Avatar"
    )
```

---

### 1.5 Обработка загрузки файла в View

```python
def registrate(request):
    if request.method == 'POST':
        form = RegisterForm(
            request.POST,           # Данные формы
            request.FILES           # Загруженные файлы
        )
        
        if form.is_valid():
            data = form.cleaned_data
            
            # Создаем пользователя
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            # Создаем профиль
            profile = Profile.objects.create(
                user=user,
                nick_name=data['nick_name']
            )
            
            # Добавляем аватар если загружен
            if data['avatar']:
                profile.avatar = data['avatar']
                profile.save()
            
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})
```

**Важно:**
- Используем `request.FILES` для доступа к загруженным файлам
- Форма должна иметь `enctype="multipart/form-data"`
- Django автоматически сохраняет файл на диск

---

### 1.6 Отображение аватара в шаблоне

```html
<!-- Отображение аватара пользователя -->
<div class="avatar-box">
    {% if user.profile.avatar %}
        <!-- Если аватар загружен - показываем его -->
        <img src="{{ MEDIA_URL }}{{ user.profile.avatar }}">
    {% else %}
        <!-- Иначе показываем изображение по умолчанию -->
        <img src="{% static 'main/default.jpg' %}">
    {% endif %}
</div>

<!-- Или более простой способ (recommended) -->
<div class="avatar-box">
    {% if user.profile.avatar %}
        <img src="{{ user.profile.avatar.url }}">
    {% else %}
        <img src="{% static 'main/default.jpg' %}">
    {% endif %}
</div>
```

**Свойства ImageField объекта:**
- `.url` - полный URL к файлу
- `.path` - полный путь на диске
- `.name` - имя файла
- `.size` - размер файла в байтах

---

### 1.7 Форма в HTML с enctype

```html
<!-- enctype="multipart/form-data" обязателен для загрузки файлов -->
<form action="" method="post" class="login-form" enctype="multipart/form-data">
    {% csrf_token %}
    
    <!-- Текстовые поля -->
    {% include 'main/Layout/formFilling.html' 
        with label="Username" 
             name="username" %}
    
    <!-- Поле для загрузки файла -->
    <div class="avatar-upload-container">
        <label for="login-password" class="avatar-label">Avatar</label>
        
        <label for="avatar_input" class="file-choose-button">
            Choose
        </label>
        
        <span id="file-name" class="file-name-text">
            No file chosen
        </span>
        
        <input type="file"
               id="avatar_input"
               name="avatar"
               class="file-input-hidden"
               onchange="document.getElementById('file-name').textContent = this.files[0].name">
    </div>
    
    <button type="submit">Register</button>
</form>
```

---

## 2. 🔄 Необходимые AJAX запросы

### 2.1 Лайк/Дизлайк вопроса и ответа

**URL:** `/ajax/vote/`  
**Метод:** POST  
**Авторизация:** Требуется

#### Параметры запроса (JSON):

```json
{
    "object_id": 42,
    "object_type": "question",
    "action": "like"
}
```

**Параметры:**
- `object_id` - ID вопроса или ответа
- `object_type` - "question" или "answer"
- `action` - "like" (лайк) или "dislike" (дизлайк)

#### Ответ (JSON):

```json
{
    "rating": 15
}
```

**Или ошибка:**
```json
{
    "error": "Wrong object type"
}
```

#### JavaScript реализация:

```javascript
// Получаем CSRF token из страницы
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Обработка клика на кнопку лайка
document.querySelectorAll('.js-vote-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const objectId = this.dataset.id;
        const objectType = this.dataset.type;
        const action = this.dataset.action;
        
        try {
            const response = await fetch('/ajax/vote/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    object_id: objectId,
                    object_type: objectType,
                    action: action
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Обновляем рейтинг на странице
                const ratingElement = document.querySelector(
                    `#rating-${objectType}-${objectId}`
                );
                if (ratingElement) {
                    ratingElement.textContent = data.rating;
                }
                
                // Меняем активный класс кнопки
                this.classList.toggle('active');
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error');
        }
    });
});
```

#### Django View для обработки:

```python
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

@require_POST
@login_required
def updateLike(request):
    """
    AJAX обработчик для лайков/дизлайков
    """
    try:
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
    
    try:
        obj = Model.objects.get(pk=object_id)
    except Model.DoesNotExist:
        return JsonResponse({'error': 'Object not found'}, status=404)
    
    # Получаем ContentType для модели
    content_type = ContentType.objects.get_for_model(obj)
    
    # Проверяем существующий лайк
    existing_like = Like.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.id,
    ).first()
    
    # Определяем новое значение
    new_value = 1 if action == 'like' else -1
    
    # Логика toggle лайков
    if existing_like:
        if existing_like.value == new_value:
            # Удаляем если тот же лайк
            existing_like.delete()
        else:
            # Меняем на противоположный
            existing_like.value = new_value
            existing_like.save()
    else:
        # Создаем новый лайк
        Like.objects.create(
            content_type=content_type,
            user=user,
            object_id=obj.id,
            value=new_value
        )
    
    # Вычисляем новый рейтинг
    new_rating = obj.likes.aggregate(
        total=Sum('value')
    )['total'] or 0
    
    return JsonResponse({'rating': new_rating})
```

---

### 2.2 Отметка правильного ответа

**URL:** `/ajax/correct/`  
**Метод:** POST  
**Авторизация:** Требуется (только автор вопроса)

#### Параметры запроса (JSON):

```json
{
    "answer_id": 5,
    "is_correct": true
}
```

#### Ответ (JSON):

```json
{
    "status": "ok"
}
```

#### JavaScript реализация:

```javascript
// Обработка чекбокса "Correct"
document.querySelectorAll('.js-correct-btn').forEach(checkbox => {
    checkbox.addEventListener('change', async function() {
        const answerId = this.dataset.answerId;
        const isCorrect = this.checked;
        
        try {
            const response = await fetch('/ajax/correct/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    answer_id: answerId,
                    is_correct: isCorrect
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                console.log('Answer marked as ' + (isCorrect ? 'correct' : 'incorrect'));
                // Визуальное обновление (класс correct-answer)
                const answerElement = document.querySelector(
                    `#answer-${answerId}`
                );
                if (isCorrect) {
                    answerElement.classList.add('correct-answer');
                } else {
                    answerElement.classList.remove('correct-answer');
                }
            } else {
                this.checked = !this.checked;  // Отменяем изменение
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            this.checked = !this.checked;  // Отменяем изменение
            alert('Network error');
        }
    });
});
```

#### Django View для обработки:

```python
@require_POST
@login_required
def updateCorrect(request):
    """
    AJAX обработчик для отметки правильного ответа
    Только автор вопроса может выбирать правильный ответ
    """
    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        is_correct = data.get('is_correct')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    try:
        answer = Answer.objects.get(pk=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'Answer not found'}, status=404)
    
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

## 3. 🔒 Обработка AJAX запросов

### 3.1 Обработка ошибок

Так как отображение ошибок при AJAX запросах затруднительно (нет перезагрузки интерфейса), желательно не давать пользователю возможность делать неправильные запросы.

#### Пример защиты на JavaScript:

```javascript
// Скрыть чекбокс если пользователь не автор вопроса
const correctMarker = document.querySelector('.correct-marker');

// Скрыть если не авторизован
if (!isUserAuthenticated) {
    if (correctMarker) {
        correctMarker.style.display = 'none';
    }
}

// Закрыть если не автор вопроса
if (!isQuestionAuthor) {
    const checkboxes = document.querySelectorAll('.js-correct-btn');
    checkboxes.forEach(cb => cb.disabled = true);
}
```

#### Правильная обработка ошибок на сервере:

```python
# Проверяем все условия ДО обновления
if not request.user.is_authenticated:
    return JsonResponse({'error': 'Not authenticated'}, status=401)

if question.user.user != request.user:
    return JsonResponse({'error': 'No permission'}, status=403)

# Если все проверки пройдены - обновляем данные
answer.is_correct = is_correct
answer.save()

return JsonResponse({'status': 'ok'}, status=200)
```

---

### 3.2 JsonResponse

Для отправки AJAX запросов в браузере используется `JsonResponse`:

```python
from django.http import JsonResponse

# Успешный ответ
return JsonResponse({'rating': 15})

# С кодом статуса
return JsonResponse({'status': 'ok'}, status=200)

# Ошибка
return JsonResponse({'error': 'Invalid data'}, status=400)

# Можно передавать списки и вложенные структуры
return JsonResponse({
    'success': True,
    'data': [1, 2, 3],
    'metadata': {
        'count': 3,
        'type': 'questions'
    }
})
```

---

### 3.3 CSRF token в AJAX запросах

Django требует CSRF token даже для AJAX POST запросов:

#### Способ 1: Из cookies

```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({...})
});
```

#### Способ 2: Из DOM элемента

```javascript
// Django добавляет token в страницу
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({...})
});
```

#### Способ 3: С помощью jQuery (если используется)

```javascript
// jQuery автоматически добавляет CSRF token
$.ajax({
    type: 'POST',
    url: '/api/endpoint/',
    data: JSON.stringify({...}),
    contentType: 'application/json',
    success: function(data) {
        console.log(data);
    }
});
```

---

## 4. 📊 Таблица AJAX endpoints

| URL | Метод | Авторизация | Параметры | Ответ |
|-----|-------|-------------|-----------|-------|
| `/ajax/vote/` | POST | ✓ | object_id, object_type, action | rating или error |
| `/ajax/correct/` | POST | ✓ (автор) | answer_id, is_correct | status или error |
| `/ajax/search/` | GET | - | q (query) | results (массив) |

---

## 5. 🎨 Обновление UI при AJAX ответе

```javascript
fetch('/ajax/vote/', {
    method: 'POST',
    headers: {...},
    body: JSON.stringify({...})
})
.then(response => response.json())
.then(data => {
    // Обновляем рейтинг на странице
    const ratingElement = document.querySelector('#rating-question-42');
    if (ratingElement) {
        ratingElement.textContent = data.rating;
    }
    
    // Добавляем/убираем класс active для кнопки
    const button = document.querySelector('[data-id="42"]');
    if (button) {
        button.classList.toggle('active');
    }
})
.catch(error => {
    console.error('Error:', error);
    alert('Something went wrong');
});
```

---

## ✨ Особенности реализации

✅ **ImageField** - встроенная поддержка загрузки файлов  
✅ **AJAX без перезагрузки** - асинхронные запросы через fetch API  
✅ **JSON ответы** - использование JsonResponse  
✅ **CSRF защита** - обязательна для POST запросов  
✅ **Обработка ошибок** - правильные HTTP статусы (400, 403, 404)  
✅ **Валидация на сервере** - проверка прав доступа  
✅ **UI обновление** - изменение класса и содержимого без перезагрузки  
✅ **Удобство пользователя** - интерактивная работа без задержек

---

## 🚀 Использованные технологии

- **Загрузка файлов**: Django ImageField, MultipartFormData
- **AJAX**: Fetch API (современный стандарт)
- **JSON**: Сериализация данных
- **CSRF**: Django middleware защита
- **HTTP статусы**: 200, 400, 403, 404
- **JavaScript**: Async/Await, Promises

---

## 📝 Чек-лист для реализации

- [ ] Настроить MEDIA_ROOT и MEDIA_URL в settings.py
- [ ] Добавить ImageField в Profile модель
- [ ] Добавить ImageField в RegisterForm и SettingsForm
- [ ] Реализовать updateLike view с AJAX обработкой
- [ ] Реализовать updateCorrect view с проверкой прав
- [ ] Написать JavaScript обработчики для кнопок лайков
- [ ] Написать JavaScript обработчик для чекбокса "Correct"
- [ ] Добавить CSRF token в AJAX запросы
- [ ] Тестировать загрузку аватаров
- [ ] Тестировать AJAX запросы в браузере

---

**Дата создания:** 17.04.2026  
**Разработчик:** Бусыгин А.Д. ИУ5-46Б
