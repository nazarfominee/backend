# Використовуємо базовий образ Python 3.9
FROM python:3.9

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо requirements.txt і встановлюємо залежності
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо усі файли проекту в контейнер
COPY . .

# Окрема змінна для шляху до конфігурації
ENV CONFIG_PATH=/app/config.json

# Запускаємо програму
CMD ["python", "middleware.py"]
