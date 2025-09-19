# Используем официальный Python
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Копируем файлы проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск бота
CMD ["python3", "bot_full.py"]
