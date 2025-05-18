Remooovy - это современное веб-приложение с биллинговой системой, которое позволяет легко и быстро удалять фон с изображений, используя модели машинного обучения.

## Основные возможности

- Удаление фона с помощью трех различных моделей
- Загрузка обработанного изображения на ПК
- Возможность регистрации и авторизации пользователей
- Сохранение истории транзакций

## Стек технологий

- Streamlit
- FastAPI
- OAuth2 authorization
- HTTP-requests
- PostgreSQL

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

### Страница приветствия

![image](https://github.com/user-attachments/assets/9f5b2d0b-5654-4bc3-8a80-e77b2129db0e)

## Страницы, доступные неавторизованному пользователю

### Страница авторизации

![image](https://github.com/user-attachments/assets/3e11b595-8d26-42aa-89ee-0a71e658d30a)

## Страница регистрации

![image](https://github.com/user-attachments/assets/f6341b98-4153-4049-bc3d-1448b6759ae1)

При попытке войти в главную страницу или страницу транзакций появится уведомление о неавторизованности. Приложение автоматически перенаправит пользователя на страницу авторизации:

![image](https://github.com/user-attachments/assets/3114ec59-6545-41c1-ae1d-ca763dbbdc42)

## Страницы, доступные авторизованному пользователю

После успешной авторизации в localstoradge появляется уникальный токен пользователя:

![image](https://github.com/user-attachments/assets/068078f2-39d5-4341-8ec6-ed12d60b7caa)

С сохранением пользователя в сессии возникли проблемы, т.к. фреймворк Streamlit не позволяет напрямую получать доступ к localstoradge. Использовался кастомный [Streamlit-local-storadge](https://pypi.org/project/streamlit-local-storage/)

## Главная страница

![image](https://github.com/user-attachments/assets/bbd9cde8-e497-407a-848e-72f1812522c1)

## Страница транзакций

![image](https://github.com/user-attachments/assets/d772169f-df55-42e4-8d48-e70528e492e1)

## Как пополнять баланс? Давайте сыграем в игру...

![image](https://github.com/user-attachments/assets/bb541a82-fc88-4523-8726-5564cb8bcb0d)

При нажатии на кнопку пополнения баланса пользователю требуется угадать число (при неугадывании ничего страшного не произойдет, система даже даст подсказку):

![image](https://github.com/user-attachments/assets/e08985c5-080a-4d6d-85c8-88d1117a04d5)

## Работа моделей
Исходное изображение:

![image](https://github.com/user-attachments/assets/38d59b7b-2087-419a-9370-15a4f7169dd1)

1) DeepLabV3
![image](https://github.com/user-attachments/assets/c010e226-2aea-4a6b-82fd-bbf620673cd2)
2) BGRM-1.4
![image](https://github.com/user-attachments/assets/892a3181-705e-44fa-935d-ff78304684d4)
3) BGRM-2.0
![image](https://github.com/user-attachments/assets/4f8d39b1-8584-4acd-bd2e-a66403364b53)

Более сложная сцена:
![image](https://github.com/user-attachments/assets/8dcfcf0a-5f09-4fd1-a04c-ecfc1c3a37dc)

1) DeepLabV3
![image](https://github.com/user-attachments/assets/c24cb664-754f-4ee1-9149-9d80e9e23b5f)
2) BGRM-1.4
![image](https://github.com/user-attachments/assets/04a4ab3a-eac1-4c57-a20b-09b18d6ec98e)
3) BGRM-2.0
![image](https://github.com/user-attachments/assets/ede0307b-bb02-42eb-8333-7c0fc6fe9c11)
