# Лабораторная работа №7: Дополнительные функции

## 📋 Описание

Реализация продвинутых функций веб-приложения: real-time сообщения через WebSocket, кэширование данных с Redis, фоновые задачи и полнотекстовый поиск по базе данных.

**Цель:** Исследование технологии Comet и механизма кэширования данных. Получение навыков работы с асинхронными операциями и оптимизацией базы данных.

---

## 1. 🔄 Real-time сообщения (Comet/WebSocket)

### Описание реализации

Необходимо реализовать рассылку мгновенных сообщений о новых ответах всем пользователям, находящимся на странице определенного вопроса. Используется технология WebSocket через сервер Centrifugo.

#### 1.1 Концепция работы

**Сценарий:**
- Пользователь A и B открыли страницу `/question/33`
- Пользователь A добавляет новый ответ
- Пользователь B должен увидеть новый ответ БЕЗ перезагрузки страницы

#### 1.2 Установка и настройка Centrifugo

```bash
# Установка Centrifugo (подробнее на centrifugo.dev)
# Для Ubuntu/Linux
wget https://github.com/centrifugal/centrifugo/releases/download/v4.0.0/centrifugo_4.0.0_linux_amd64.tar.gz
tar -xzf centrifugo_4.0.0_linux_amd64.tar.gz
./centrifugo --config=config.json
```

#### 1.3 Конфиг Centrifugo

**Файл:** `centrifugo/config.json`

```json
{
  "v3_use_offset": true,
  "token_hmac_secret_key": "your-secret-key",
  "admin_password": "admin-password",
  "admin_secret": "admin-secret",
  "api_key": "api-secret-key",
  "allowed_origins": ["*"],
  "port": 8000,
  "engine": "memory"
}
```

#### 1.4 JavaScript библиотека Centrifugo

На странице вопроса добавить JavaScript обработчик:

```html
<!-- Подключаем Centrifugo библиотеку -->
<script src="https://cdn.jsdelivr.net/npm/centrifuge@5.0.0/dist/centrifuge.min.js"></script>

<script>
    // Получаем токен для подключения
    const tokenData = JSON.parse(
        document.getElementById('centrifugo-token-data').textContent
    );
    
    // Подключаемся к Centrifugo
    const client = new Centrifuge('ws://localhost:8000/connection/websocket');
    
    // Получаем ID вопроса
    const questionId = document.querySelector('[data-question-id]').dataset.questionId;
    
    // Подписываемся на канал вопроса
    const subscription = client.getSubscription(`question:${questionId}`);
    
    subscription.on('publication', function(ctx) {
        // Получили новое сообщение от сервера
        const data = ctx.data;
        
        // Добавляем новый ответ в список
        const answerHtml = data.html;
        document.querySelector('.answers-section').insertAdjacentHTML('beforeend', answerHtml);
    });
    
    subscription.subscribe();
    client.connect();
</script>
```

#### 1.5 Django View для отправки сообщения в Centrifugo

```python
from cent import Client, PublishRequest
from SegmentationFault.settings import CENTRIFUGO_API_URL, CENTRIFUGO_API_KEY

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
            
            # Генерируем HTML нового ответа
            answer_html = render_to_string(
                'main/Layout/answer.html',
                {'answer': answer},
                request=request
            )
            
            # Отправляем сообщение в Centrifugo
            try:
                client = Client(
                    CENTRIFUGO_API_URL, 
                    api_key=CENTRIFUGO_API_KEY, 
                    timeout=1
                )
                
                request_data = PublishRequest(
                    channel=f"question:{question_id}",
                    data={'html': answer_html}
                )
                
                client.publish(request_data)
            except Exception as err:
                print(f"Centrifugo error: {err}")
            
            # Редирект на страницу вопроса с якорем
            url = reverse('question', args=[question.pk])
            return redirect(f"{url}?page={1}#answer-{answer.id}")
    else:
        form = AnswerForm()
    
    # ... остальной код view
```

#### 1.6 Особенности реализации:

✅ Настроить сервер Centrifugo  
✅ Добавить JavaScript обработчик Centrifugo сервера  
✅ В форме добавления ответа добавить код, отправляющий сообщения в Centrifugo  
✅ Использовать библиотеку requests для отправки сообщений

---

## 2. 💾 Кэширование и фоновый запуск

### Описание реализации

Необходимо подготовить и вывести данные для правой колонки (лучшие пользователи, популярные теги). Поскольку запросы на предполагаются тяжелыми, необходимо кэшировать данные на диске или memcached.

#### 2.1 Требования

**Данные для кэширования:**
- **Популярные теги** - 10 тегов с самым большим количеством вопросов за последние 3 месяца
- **Лучшие пользователи** - 10 пользователей задавших самые популярные вопросы или давших самые популярные ответы за последнюю неделю

#### 2.2 Кэширование с Django

```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page

# Способ 1: Ручное кэширование
def get_best_tags():
    # Проверяем кэш
    cached_tags = cache.get('best_tags')
    
    if cached_tags is not None:
        return cached_tags
    
    # Если кэша нет - выполняем запрос
    from datetime import timedelta
    from django.utils import timezone
    
    three_months_ago = timezone.now() - timedelta(days=90)
    
    best_tags = Tag.objects.annotate(
        count_questions=Count('questions', 
                            filter=Q(questions__created_at__gte=three_months_ago))
    ).order_by('-count_questions')[:10]
    
    # Кэшируем на 1 час
    cache.set('best_tags', list(best_tags), 3600)
    
    return best_tags

# Способ 2: Декоратор кэширования
@cache_page(3600)  # Кэшировать на 1 час
def index(request):
    best_tags = get_best_tags()
    best_users = get_best_users()
    
    return render(request, 'index.html', {
        'best_tags': best_tags,
        'best_users': best_users,
    })
```

#### 2.3 Конфигурация Redis в settings.py

```python
# settings.py

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### 2.4 Management Command для обновления кэша

Необходимо создать Management Command, запускаемый из Cron для обновления кэша.

**Файл:** `app/management/commands/update_cache.py`

```python
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from app.models import Tag, Profile

class Command(BaseCommand):
    help = 'Update cached data (best tags, best users)'
    
    def handle(self, *args, **options):
        self.stdout.write("Updating cache...")
        
        # Обновляем лучшие теги
        three_months_ago = timezone.now() - timedelta(days=90)
        
        best_tags = Tag.objects.annotate(
            count_questions=Count('questions', 
                                filter=Q(questions__created_at__gte=three_months_ago))
        ).order_by('-count_questions')[:10]
        
        cache.set('best_tags', list(best_tags), 3600)
        self.stdout.write("✓ Best tags updated")
        
        # Обновляем лучших пользователей
        last_week = timezone.now() - timedelta(days=7)
        
        best_users = Profile.objects.annotate(
            count_questions=Count('user_questions', distinct=True,
                                filter=Q(user_questions__created_at__gte=last_week))
        ).annotate(
            count_answers=Count('user_answers', distinct=True,
                              filter=Q(user_answers__created_at__gte=last_week))
        ).annotate(
            count_activities=F('count_questions') + F('count_answers')
        ).order_by('-count_activities')[:10]
        
        cache.set('best_users', list(best_users), 3600)
        self.stdout.write("✓ Best users updated")
        
        self.stdout.write(self.style.SUCCESS('Cache updated successfully!'))
```

#### 2.5 Cron job для фонового запуска

```bash
# Добавить в crontab
crontab -e

# Выполнять каждый час
0 * * * * cd /path/to/project && python manage.py update_cache
```

#### 2.6 Использование кэшированных данных в view

```python
from django.core.cache import cache

def index(request):
    # Получаем из кэша
    best_tags = cache.get('best_tags', [])
    best_users = cache.get('best_users', [])
    
    # Если кэша нет (первый запуск) - вычисляем
    if not best_tags:
        best_tags = Tag.objects.best()
        cache.set('best_tags', list(best_tags), 3600)
    
    if not best_users:
        best_users = Profile.objects.best()
        cache.set('best_users', list(best_users), 3600)
    
    return render(request, 'index.html', {
        'best_tags': best_tags,
        'best_users': best_users,
    })
```

#### 2.7 Особенности реализации:

✅ Кэширование данных на диске или memcached  
✅ Вывода данных для правой колонки (кэшированные данные)  
✅ Не запускать вывод этих запросов в каждой выышке  
✅ Брать данные из кэша  
✅ Заполнять кэш данными с помощью Management команды, запускаемой из Cron

---

## 3. 🔍 Полнотекстовый поиск

### Описание реализации

Необходимо реализовать поиск по заголовкам и содержимому вопросов. Пользователь вводит текст в поисковую строку, которая находится в шапке. По введенному тексту СУБД должна находить совпадения, используя полнотекстовые индексы.

#### 3.1 Использование PostgreSQL Full-Text Search

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q

def searchItem(request):
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Полнотекстовый поиск с взвешиванием
    search_vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
    search_query = SearchQuery(query)
    
    # Результаты с высоким рейтингом релевантности
    full_find_objects = Question.objects.annotate(
        rank=SearchRank(search_vector, search_query)
    ).filter(rank__gte=0.1).order_by('-rank')
    
    # Fallback поиск через LIKE
    similar_find_objects = Question.objects.filter(
        Q(title__icontains=query) | Q(text__icontains=query)
    )
    
    # Объединяем результаты
    list_objects = (full_find_objects | similar_find_objects).distinct().order_by('-id')[:5]
    
    data = [
        {
            'id': q.id,
            'title': q.title,
        } for q in list_objects
    ]
    
    return JsonResponse({'results': data})
```

#### 3.2 Триггеры для автоматического обновления индексов

```sql
-- В PostgreSQL создаем триггер для автоматического обновления индекса
CREATE OR REPLACE FUNCTION update_search_index() RETURNS trigger AS $$
BEGIN
    NEW.search_vector = to_tsvector('russian', NEW.title) || 
                        to_tsvector('russian', NEW.text);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER question_search_update BEFORE INSERT OR UPDATE ON app_question
    FOR EACH ROW EXECUTE FUNCTION update_search_index();
```

#### 3.3 JavaScript для поиска в реальном времени

```javascript
// При вводе в поиск
document.querySelector('#search-input').addEventListener('input', async function(e) {
    const query = e.target.value;
    
    if (query.length < 2) {
        document.querySelector('#search-results').innerHTML = '';
        return;
    }
    
    // Отправляем запрос поиска
    const response = await fetch(`/ajax/search/?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    
    // Отображаем результаты
    let html = '';
    for (const result of data.results) {
        html += `<a href="/question/${result.id}/" class="dropdown-item">${result.title}</a>`;
    }
    
    document.querySelector('#search-results').innerHTML = html;
    document.querySelector('#search-results').classList.add('show');
});
```

#### 3.4 Требования к поиску:

✅ Поиск работает по заголовкам и содержимому вопросов  
✅ Результаты поиска ранжируются по релевантности  
✅ Используются полнотекстовые индексы СУБД  
✅ Результаты отображаются пользователю в виде выпадающего списка  
✅ Запрос должен отправляться автоматически по мере ввода пользователем частей текста  
✅ Не должны перегружаться сервер лишними запросами, отправляя запрос на каждый новый введенный символ во время печати

---

## 📊 Итоговая таблица функций

| Функция | Технология | Использование |
|---------|-----------|---------------|
| Real-time | Centrifugo WebSocket | Отправка новых ответов |
| Кэширование | Redis + Django Cache | Популярные теги, лучшие пользователи |
| Фоновые задачи | Management Command + Cron | Обновление кэша |
| Полнотекстовый поиск | PostgreSQL Full-Text Search | Поиск вопросов |

---

## 🔐 Продвинутые концепции

### Redis для кэширования

```python
# Простое кэширование
from django_redis import get_redis_connection

redis_conn = get_redis_connection("default")

# Установить значение
redis_conn.set('key', 'value', 3600)  # TTL 1 час

# Получить значение
value = redis_conn.get('key')

# Удалить значение
redis_conn.delete('key')

# Инкрементировать счетчик
redis_conn.incr('counter')
```

### Celery для фоновых задач (опционально)

```python
from celery import shared_task

@shared_task
def update_cache_task():
    """Обновить кэш в фоновой задаче"""
    from django.core.cache import cache
    from django.db.models import Count
    
    best_tags = Tag.objects.annotate(
        count=Count('questions')
    ).order_by('-count')[:10]
    
    cache.set('best_tags', list(best_tags), 3600)
    return 'Cache updated'

# Вызвать задачу
update_cache_task.delay()
```

### WebSocket события в реальном времени

```javascript
// Слушаем события от сервера
const eventSource = new EventSource('/api/events/');

eventSource.addEventListener('new_answer', function(event) {
    const data = JSON.parse(event.data);
    console.log('New answer:', data);
});

eventSource.addEventListener('error', function(event) {
    console.error('Connection error:', event);
});
```

---

## ✨ Особенности реализации

✅ **Real-time WebSocket** - Centrifugo для мгновенных сообщений  
✅ **Redis кэширование** - для быстрого доступа к популярным данным  
✅ **Management Command** - автоматическое обновление кэша  
✅ **Cron jobs** - фоновый запуск задач по расписанию  
✅ **Full-Text Search** - полнотекстовый поиск с индексами  
✅ **Fallback поиск** - LIKE как резервный вариант  
✅ **Асинхронные операции** - неблокирующие запросы  
✅ **Масштабируемость** - готовность к большим нагрузкам

---

## 🚀 Использованные технологии

- **Centrifugo** - WebSocket сервер для real-time
- **Redis** - in-memory кэширование
- **PostgreSQL** - Full-Text Search
- **Django Cache Framework** - встроенное кэширование
- **Management Commands** - фоновые задачи
- **Cron** - планирование задач
- **Celery** (опционально) - асинхронная очередь задач

---

## 📝 Чек-лист для реализации

- [ ] Установить и настроить Centrifugo
- [ ] Подключить JavaScript библиотеку Centrifugo
- [ ] Реализовать отправку новых ответов через Centrifugo
- [ ] Установить Redis
- [ ] Настроить Django кэширование с Redis
- [ ] Реализовать кэширование для популярных тегов
- [ ] Реализовать кэширование для лучших пользователей
- [ ] Создать Management Command для обновления кэша
- [ ] Настроить Cron для регулярного запуска
- [ ] Реализовать полнотекстовый поиск PostgreSQL
- [ ] Написать JavaScript обработчик поиска
- [ ] Тестировать real-time сообщения
- [ ] Проверить кэширование
- [ ] Проверить поиск по различным запросам

---

## 🎓 Выводы

Эта лабораторная работа охватывает продвинутые техники оптимизации и функциональности современного веб-приложения:

1. **Real-time коммуникация** - важна для интерактивных приложений
2. **Кэширование** - критично для масштабируемости
3. **Фоновые задачи** - позволяют не блокировать основной поток
4. **Полнотекстовый поиск** - улучшает UX

Комбинация этих технологий позволяет создавать высокопроизводительные приложения с хорошим пользовательским опытом.

---

**Дата создания:** 17.04.2026  
**Разработчик:** Бусыгин А.Д. ИУ5-46Б
