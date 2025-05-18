Remooovy - это современное веб-приложение с биллинговой системой, которое позволяет легко и быстро удалять фон с изображений, используя модели машинного обучения.

## Основные возможности

- Удаление фона с помощью трех различных моделей
- Загрузка обработанного изображения на ПК
- Возможность регистрации и авторизации пользователей
- Сохранение истории транзакций

## Структура проекта

```
BGRemover/
├── app/                        # Backend приложение
│   ├── api/                   # API endpoints и маршрутизация
│   ├── core/                  # Ядро приложения
│   │   ├── config.py         # Конфигурация приложения
│   │   ├── database.py       # Настройки базы данных
│   │   └── security.py       # Безопасность и JWT
│   ├── models/               # SQLAlchemy модели
│   ├── schemas/              # Pydantic схемы
│   ├── Dockerfile           # Dockerfile для бэкенда
│   └── main.py              # Точка входа FastAPI приложения
│
├── frontend/                  # Frontend приложение
│   ├── pages/               # Страницы приложения
│   ├── assets/             # Статические файлы
│   ├── utils/              # Вспомогательные функции
│   ├── Dockerfile         # Dockerfile для фронтенда
│   └── config.py          # Конфигурация фронтенда
│
├── background_removal/        # Модуль удаления фона
│   └── models/              # ML модели для обработки изображений
│
├── scripts/                   # Вспомогательные скрипты
│
├── docker-compose.yml         # Docker конфигурация
├── pyproject.toml            # Poetry зависимости
├── poetry.lock               # Poetry лок-файл
└── .env.example              # Пример переменных окружения
```

## ERD-диаграмма

![image](https://github.com/user-attachments/assets/bf66e66f-e7b5-435e-8721-ce6aba2621b8)

## Используемые модели

1. [DeepLabV3](https://docs.pytorch.org/vision/stable/_modules/torchvision/models/segmentation/deeplabv3.html)
2. [RMBG-1.4](https://huggingface.co/briaai/RMBG-1.4)
3. [RMBG-2.0](https://huggingface.co/briaai/RMBG-2.0)

## Описание API

![image](https://github.com/user-attachments/assets/2d880e81-a6e6-44c5-8552-c2de4d91368d)

## Руководство пользователя


