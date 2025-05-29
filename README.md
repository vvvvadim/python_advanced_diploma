<<<<<<< HEAD
# python_advanced_diploma
=======
# Python Advanced Diploma Project

## Описание проекта
Проект представляет собой API для работы с базой данных, реализованный с использованием FastAPI и SQLAlchemy. API предоставляет эндпоинты для выполнения SQL-запросов и управления базой данных.

## Требования
- Python 3.8+
- PostgreSQL 15+
- Docker (опционально)

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd python_advanced_diploma
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл, указав необходимые параметры
```

4. Запустите приложение:
```bash
uvicorn api.main:app --reload
```

## API Endpoints

### Аутентификация

#### POST /api/v1/auth
Аутентификация пользователя по API ключу.

**Заголовки:**
- `X-API-Key`: API ключ пользователя

**Ответ:**
```json
{
    "access_tokaen": "string",
    "token_type": "bearer"
}
```

### База данных

#### POST /api/v1/database/query
Выполнение SQL-запроса к базе данных.

**Заголовки:**
- `Authorization`: Bearer token

**Тело запроса:**
```json
{
    "query": "string"  // SQL запрос
}
```

**Ответ:**
```json
{
    "result": [
        {
            "column1": "value1",
            "column2": "value2"
        }
    ]
}
```

#### GET /api/v1/database/tables
Получение списка всех таблиц в базе данных.

**Заголовки:**
- `Authorization`: Bearer token

**Ответ:**
```json
{
    "tables": [
        "table1",
        "table2"
    ]
}
```

#### GET /api/v1/database/table/{table_name}
Получение структуры указанной таблицы.

**Заголовки:**
- `Authorization`: Bearer token

**Параметры пути:**
- `table_name`: Имя таблицы

**Ответ:**
```json
{
    "columns": [
        {
            "name": "column1",
            "type": "string",
            "nullable": true
        }
    ]
}
```

## Тестирование

Для запуска тестов используйте:
```bash
pytest -v --asyncio-mode=strict
```

## Docker

Для запуска в Docker:
```bash
docker-compose up --build
```

## Безопасность

- Все запросы к базе данных требуют аутентификации
- Используется JWT для авторизации
- SQL-запросы проходят валидацию перед выполнением
- Поддерживается ограничение доступа к определенным таблицам

## Обработка ошибок

API возвращает следующие коды ошибок:
- 400: Неверный запрос
- 401: Не авторизован
- 403: Доступ запрещен
- 404: Ресурс не найден
- 500: Внутренняя ошибка сервера

## Логирование

Все операции с базой данных логируются для аудита и отладки. Логи доступны в директории `logs/`. 
>>>>>>> 2f44ad2 (full)
