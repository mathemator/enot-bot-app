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
ENV API_ID=23251633
ENV API_HASH=a4feaab630f57fea704d48075ffe685f
ENV BOT_TOKEN=7482518493:AAGOw-959ow3GSwVJiSTRMdL4RZ2eONaUEU

# Устанавливаем переменную окружения для корректного вывода в консоли
ENV PYTHONUNBUFFERED=1

# Запускаем оба процесса
CMD ["sh", "-c", "alembic upgrade head && python /app/src/bot/bot_app.py & python /app/src/app/app.py"]