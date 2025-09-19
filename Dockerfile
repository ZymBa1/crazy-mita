# Используем официальный Python 3.11
FROM python:3.11-slim

# Создаем рабочую папку
WORKDIR /app

# Копируем файлы
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Переменные окружения можно подключить через Fly.io
ENV TELEGRAM_TOKEN=$TELEGRAM_TOKEN
ENV HF_API_KEY=$HF_API_KEY
ENV ADMIN_USER_ID=$ADMIN_USER_ID

# Команда для запуска бота
CMD ["python3", "bot_full.py"]
