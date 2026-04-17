# Лабораторная работа №6: Настройка веб-серверов

## 📋 Описание

Подготовка инфраструктуры для развертывания Django приложения и обучение настройке веб-серверов. Настройка gunicorn для запуска WSGI скриптов, nginx для отдачи статического контента и проксирования запросов. Тестирование производительности различных конфигураций.

**Цель:** Подготовить инфраструктуру для будущего проекта и научиться настраивать веб-серверы.  
**Важное замечание:** Вместо `pupkin` используйте свою фамилию!

---

## 1. 🚀 Настройка gunicorn для запуска WSGI скриптов

### Описание реализации

Gunicorn (Green Unicorn) - это WSGI HTTP сервер для Python приложений. Он нужен для запуска Django приложения в продакшене.

#### 1.1 Установка gunicorn

```bash
pip install gunicorn
```

#### 1.2 Конфигурация gunicorn

Согласно документации Gunicorn, создайте конфигурационный файл, который запустит ваше приложение с двумя процессами-воркерами.

**Файл:** `gunicorn/config.py`

```python
# Количество рабочих процессов
workers = 2

# Тип воркеров (sync - синхронный, по умолчанию)
worker_class = 'sync'

# Порт на котором слушать
bind = '127.0.0.1:8000'

# Лог ошибок
errorlog = '-'

# Лог доступа
accesslog = '-'

# Уровень логирования
loglevel = 'info'

# Timeout для воркеров (в секундах)
timeout = 30

# Максимальное количество запросов перед перезагрузкой воркера
max_requests = 1000

# Случайный разброс max_requests
max_requests_jitter = 100
```

#### 1.3 Запуск приложения с gunicorn

```bash
# Простой запуск
gunicorn SegmentationFault.wsgi:application

# С конфигом
gunicorn -c gunicorn/config.py SegmentationFault.wsgi:application

# С указанием порта
gunicorn -b 127.0.0.1:8001 SegmentationFault.wsgi:application

# С указанием количества воркеров
gunicorn -w 4 SegmentationFault.wsgi:application
```

---

## 2. 📝 Создание простого WSGI-скрипта

### Описание реализации

WSGI-скрипт - простая функция или класс, который может работать независимо от Django приложения. Используется для тестирования производительности веб-сервера.

#### 2.1 Простой WSGI скрипт

**Файл:** `ask_pupkin/wsgi_simple.py` (замените `pupkin` на вашу фамилию)

```python
"""
Простой WSGI-скрипт для тестирования производительности gunicorn.
"""

def application(environ, start_response):
    """
    Простое WSGI приложение которое возвращает текст.
    
    Args:
        environ: словарь переменных окружения
        start_response: функция для отправки заголовков ответа
    
    Returns:
        список с телом ответа
    """
    
    # Получаем путь из переменной окружения
    path = environ.get('PATH_INFO', '/')
    
    # Получаем метод запроса
    method = environ.get('REQUEST_METHOD', 'GET')
    
    # Получаем параметры запроса
    query_string = environ.get('QUERY_STRING', '')
    
    # Строим тело ответа
    response_body = f"""
    <html>
        <head>
            <title>Simple WSGI App</title>
        </head>
        <body>
            <h1>Simple WSGI Application</h1>
            <p>Method: {method}</p>
            <p>Path: {path}</p>
            <p>Query: {query_string}</p>
        </body>
    </html>
    """.encode('utf-8')
    
    # Отправляем заголовки ответа
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)
    
    # Возвращаем тело ответа
    return [response_body]
```

#### 2.2 Запуск WSGI скрипта

```bash
# Запуск на порту 8001
gunicorn -b 127.0.0.1:8001 ask_pupkin.wsgi_simple:application

# Тестирование
curl http://127.0.0.1:8001/
```

#### Требования к WSGI-скрипту:
✅ Запускается с помощью gunicorn  
✅ Выводит список переданных GET и POST параметров  
✅ Выполняется при запросе `localhost:8081`  
✅ Работает без использования Django

---

## 3. 🏗️ Настройка nginx для отдачи статического контента

### Описание реализации

Nginx эффективнее Django для отдачи статических файлов. Необходимо настроить nginx следующим образом:

#### 3.1 Структура статических файлов

```
ask_pupkin/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── uploads/
    └── (загруженные пользователями файлы)
```

#### 3.2 Конфигурация nginx

**Файл:** `/etc/nginx/sites-available/ask_pupkin`

```nginx
server {
    listen 80;
    server_name localhost;
    
    # Отдача статических файлов напрямую из ask_pupkin/static
    location /static/ {
        alias /path/to/ask_pupkin/static/;
        
        # Кэширование на клиенте на 30 дней
        expires 30d;
        
        # Отключаем access log для статики
        access_log off;
    }
    
    # Отдача загруженных файлов
    location /uploads/ {
        alias /path/to/ask_pupkin/uploads/;
        
        # Кэширование на клиенте на 7 дней
        expires 7d;
    }
    
    # Все остальное идет на gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3.3 Требования к nginx конфигурации:

✅ Все файлы с URL начинающимися с `/uploads/` отдаются из `ask_pupkin/uploads`  
✅ Все файлы с расширением `.js`, `.css`, `.jpeg` и т.д. отдаются из `ask_pupkin/static`  
✅ Файлы отдаются с заголовками, кэшируя файлы на стороне браузера  
✅ Файлы сжимаются на сервере для уменьшения размера передаваемых файлов  
✅ Размер конфига nginx не должен превышать 50 строк

#### 3.4 Проверка конфигурации

```bash
# Проверить синтаксис конфига
sudo nginx -t

# Перезагрузить nginx
sudo systemctl reload nginx

# Или вручную
sudo nginx -s reload
```

---

## 4. 🔀 Настройка проксирования в nginx

### Описание реализации

Когда nginx получает запрос, который не может обработать (например, динамическую страницу), он проксирует запрос на gunicorn.

#### 4.1 Базовая конфигурация проксирования

```nginx
location / {
    # Проксируем на gunicorn сервер
    proxy_pass http://127.0.0.1:8000;
    
    # Передаем заголовки
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

#### 4.2 Upstream конфигурация (для нескольких gunicorn процессов)

```nginx
upstream gunicorn_app {
    least_conn;  # Выбираем сервер с наименьшим количеством соединений
    
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4.3 Требования к конфигурации:

✅ Настроить nginx для проксирования всех нестатических запросов (URL без расширения, например `/` или `/login/`) на gunicorn  
✅ Настроить upstream  
✅ Настроить proxy_cache и проверить его работу

---

## 5. 📊 Сравнение производительности

### Описание реализации

С помощью утилиты Apache Benchmark (`ab`) или `wrk` сравниваем производительность различных конфигураций.

#### 5.1 Установка инструментов тестирования

```bash
# Apache Benchmark (ubuntu)
sudo apt-get install apache2-utils

# Или использовать wrk (более современный вариант)
# Установка из исходников: https://github.com/wg/wrk
```

#### 5.2 Проведение измерений

Необходимо провести пять измерений:

**1. Отдача статического документа напрямую через nginx**

```bash
docker compose up --build
ab -n 1000 -c 50 http://localhost/static/main/bench_nginx.html
```

**2. Отдача статического документа напрямую через gunicorn**

```bash
uv run gunicorn -c gunicorn/config.py SegmentationFault.wsgi:application
ab -n 5000 -c 50 http://127.0.0.1:8001/static/main/bench_nginx.html
```

**3. Отдача динамического документа напрямую через gunicorn**

```bash
docker compose -f docker-compose-development.yml up --build
ab -n 5000 -c 50 http://127.0.0.1:8081/
```

**4. Отдача динамического документа через проксирование запроса с nginx на gunicorn**

```bash
docker compose -f ./docker-compose-without-cache.yml up --build
ab -n 5000 -c 50 http://localhost
```

**5. Отдача динамического документа через проксирование с nginx на gunicorn, при кэшировании ответа на nginx (proxy_cache)**

```bash
docker compose up --build
ab -n 5000 -c 50 http://localhost
```

#### 5.3 Параметры Apache Benchmark

```bash
ab -n 1000 -c 50 http://example.com

# -n 1000     : Количество запросов (1000)
# -c 50       : Количество одновременных соединений (50)
# URL         : Адрес для тестирования
```

#### 5.4 Анализ результатов

```
Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
...
Finished 1000 requests

Server Software:        nginx/1.18.0
Server Hostname:        localhost
Server Port:            80

Document Path:          /static/main/bench_nginx.html
Document Length:        1234 bytes

Concurrency Level:      50
Time taken for tests:   0.542 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      1265432 bytes
HTML transferred:       1234000 bytes

Requests per second:    1844.83 [#/sec] (mean)
Time per request:       27.10 [ms] (mean)
Time per request:       0.54 [ms] (mean, across all concurrent requests)
Transfer rate:          2276.35 [Kbytes/sec] received

Connection Times (ms)
                min  mean[+/-sd] median   max
Connect:        0    12  5.2      11      32
Processing:     5    14  6.1      13      41
Waiting:        2     8  4.5       7      28
Total:          8    27  8.3      25      60
```

**Ключевые метрики:**
- **Requests per second** - пропускная способность (чем выше, тем лучше)
- **Time per request** - время обработки одного запроса (чем ниже, тем лучше)
- **Failed requests** - количество ошибок

---

## 6. 📈 Результат выполнения домашнего задания

### Ожидаемый результат:

Результат выполнения домашнего задания включает:

1. **Директория с созданным проектом:**
   ```
   ask_pupkin/
   ├── SegmentationFault/        # Django проект
   ├── app/                       # Django приложение
   ├── gunicorn/
   │   └── config.py             # Конфиг gunicorn
   ├── static/                    # Статические файлы
   ├── manage.py
   └── requirements.txt
   ```

2. **Конфиг nginx:**
   - Готовая конфигурация nginx для отдачи статики
   - Проксирование на gunicorn
   - Proxy cache для динамических документов

3. **Конфиг gunicorn:**
   - Настроенный файл конфигурации
   - Запуск с несколькими воркерами
   - Логирование

4. **Результаты нагрузочного тестирования:**
   - Вывод утилиты `ab` для каждого из 5 измерений
   - Сравнение производительности различных конфигураций
   - Анализ результатов

---

## 📊 Таблица сравнения производительности

Ниже приведена таблица для заполнения результатов тестирования:

| Конфигурация | Requests/sec | Time per request (ms) | Failed |
|--------------|-------------|----------------------|--------|
| Статика через nginx | | | |
| Статика через gunicorn | | | |
| Динамика через gunicorn | | | |
| Динамика через nginx→gunicorn | | | |
| Динамика через nginx→gunicorn (cache) | | | |

---

## 🔍 Анализ результатов

**Вопросы на которые нужно ответить:**

1. **Насколько быстрее отдается статика по сравнению с WSGI?**
   - Обычно в 5-10 раз быстрее

2. **Во сколько раз ускоряет работу proxy_cache?**
   - Зависит от времени обработки динамического контента
   - Обычно в 2-5 раз

3. **Как проксирование влияет на производительность?**
   - Небольшое снижение (1-2%)
   - Nginx очень эффективен в проксировании

---

## 🎯 Docker Compose конфигурации

### docker-compose.yml (с кэшем)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ask_pupkin/static:/static
    depends_on:
      - gunicorn

  gunicorn:
    build: .
    command: gunicorn -b 0.0.0.0:8000 -w 2 SegmentationFault.wsgi:application
    expose:
      - "8000"
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,127.0.0.1
```

### docker-compose-without-cache.yml (без кэша)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx-no-cache.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - gunicorn

  gunicorn:
    build: .
    command: gunicorn -b 0.0.0.0:8000 -w 2 SegmentationFault.wsgi:application
    expose:
      - "8000"
```

---

## ✨ Особенности реализации

✅ **Gunicorn** - WSGI сервер для запуска Django  
✅ **Nginx** - веб-сервер для статики и проксирования  
✅ **Upstream** - балансировка нагрузки между несколькими gunicorn  
✅ **Proxy cache** - кэширование динамического контента  
✅ **Apache Benchmark** - тестирование производительности  
✅ **Docker Compose** - организация контейнеров  
✅ **WSGI скрипт** - простое приложение для тестирования

---

## 🚀 Использованные технологии

- **Gunicorn** - WSGI HTTP сервер
- **Nginx** - веб-сервер и reverse proxy
- **Docker** - контейнеризация
- **Apache Benchmark (ab)** - нагрузочное тестирование
- **Wrk** - альтернатива ab (более производительная)

---

## 📝 Чек-лист для реализации

- [ ] Установить gunicorn
- [ ] Создать конфиг gunicorn (2 воркера)
- [ ] Создать простой WSGI скрипт
- [ ] Настроить nginx для отдачи статики
- [ ] Настроить nginx для проксирования
- [ ] Настроить upstream в nginx
- [ ] Настроить proxy_cache
- [ ] Провести 5 измерений производительности
- [ ] Заполнить таблицу результатов
- [ ] Ответить на вопросы анализа

---

**Дата создания:** 17.04.2026  
**Разработчик:** Бусыгин А.Д. ИУ5-46Б
