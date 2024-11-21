# Dockerfile
FROM python:3.11-slim

# Установка необходимых утилит
RUN apt-get update && apt-get install -y netcat-openbsd

# Установка Python-зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Команда запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
