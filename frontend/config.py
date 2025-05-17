import os

# URL для API (используем значение из переменной окружения или localhost для локальной разработки)
API_URL = os.getenv("API_URL", "http://backend:8000")

# Увеличенный таймаут для обработки больших изображений (5 минут)
REQUEST_TIMEOUT = 300