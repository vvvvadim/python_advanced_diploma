# Итоговый проект Тема: «Сервис микроблогов».

Микросервисное приложение с REST API для социальной сети, разработанное в рамках дипломного проекта.

## 🚀 Быстрый старт

### Требования
- Docker 20.10+
- docker-compose 1.29+

### Установка
```bash
git clone https://https://github.com/vvvvadim/python_advanced_diploma.git

🔧 Конфигурация

Файлы окружения:

создайте файл .env в api/config с вашими настройка для подключения к БД формата:
DB_HOST="ваш адрес сервера БД"
DB_NAME="Название БД"
DB_USERNAME="Имя пользователя"
DB_PASSWORD="Пароль"
DB_PORT="порт для подключения к бд по умолчанию 5432"

📚 Документация API

После запуска доступны:

    Swagger UI: http://localhost:8000/docs

    Redoc: http://localhost:8000/redoc

🛠 Технологии
Компонент	Технология
Бэкенд	FastAPI
База данных	PostgreSQL
ORM	SQLAlchemy 2.0
Аутентификация	JWT
Тестирование	pytest
🧪 Тестирование

# Установка зависимостей
pip install -r requirements_test.txt

# Запуск тестов
pytest -v