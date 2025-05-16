# Используем базовый образ Python 3.12
FROM python:3.12-slim

# Создаем директорию ВНУТРИ контейнера, все дальнейшие операции будут выполняться в этой директории
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
COPY ./frontend /src/frontend

# Добавляем /src в PYTHONPATH
ENV PYTHONPATH=/src

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "frontend/Home.py", "--server.port=8501", "--server.address=0.0.0.0"] 