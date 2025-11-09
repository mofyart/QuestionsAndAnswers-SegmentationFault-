# Используем Python 3.12
FROM python:3.12-slim

# Устанавливаем переменные окружения, чтобы Python не буферизовал вывод
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем pip и устанавливаем uv
RUN pip install --upgrade pip
RUN pip install uv

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . .

# Открываем порт 8000
EXPOSE 8000
