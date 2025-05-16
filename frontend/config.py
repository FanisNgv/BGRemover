import os

# URL для API (используем значение из переменной окружения или localhost для локальной разработки)
API_URL = os.getenv("API_URL", "http://backend:8000")

# Настройки для запросов
REQUEST_TIMEOUT = 10  # секунды 