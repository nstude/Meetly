# Используем официальный python образ
FROM python:3.11-slim

# Устанавливаем зависимости OS
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем файлы зависимостей и устанавливаем
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем исходники
COPY . /app/

# Запускаем сервер (можно заменить на gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
