# Указываем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код и устанавливаем пакет
COPY src/ /app/src/
COPY setup.py /app/
COPY alembic.ini /app/
COPY alembic /app/alembic
COPY data /app/data

# Устанавливаем пакет
RUN pip install --no-cache-dir .

ENV DATABASE_PATH=/app/data/database.db
ENV DATABASE_URL=sqlite:///${DATABASE_PATH}
ENV API_ID=
ENV API_HASH=
ENV BOT_TOKEN=
# Устанавливаем переменную окружения для корректного вывода в консоли
ENV PYTHONUNBUFFERED=1

# Запускаем оба процесса
CMD ["sh", "-c", "alembic upgrade head && python /app/src/bot/bot.py & python /app/src/app/app.py"]