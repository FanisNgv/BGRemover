FROM python:3.12-slim

WORKDIR /src

# Установка poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Отключаем создание виртуального окружения внутри контейнера
RUN poetry config virtualenvs.create false

# Устанавливаем только зависимости (без установки проекта)
RUN poetry install --no-root --only main --no-interaction --no-ansi

# Копируем код приложения
COPY ./app /src/app

# Добавляем директорию /src в PYTHONPATH
ENV PYTHONPATH=/src

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 