# Запрос на создание Orcestator

## Цель
Создать полнофункциональный оркестратор (Orcestator), который:
* Эмулирует OpenAI-API (совместим с VS Code Copilot Agent)
* Работает на базе FastChat (контроллер + openai_api_server + кастомный воркер)
* Проксирует запросы в OpenRouter (GPT-4o / Claude 3.5 и др.)
* Ведет подробное логирование (текстовые логи + Prometheus-метрики)
* Имеет документацию по установке для Windows 11 (с Docker и без)

## Технические требования

### 1. OpenAI-совместимый API
* Поддержка эндпоинтов `/v1/models`, `/v1/chat/completions`
* Поддержка потоковой передачи данных (streaming)
* Подмена поля `model` на `"orcestator"` в ответах для совместимости с Copilot

### 2. Основной движок — FastChat
* Использование штатного `controller` и `openai_api_server`
* Создание кастомного воркера-прокси для перенаправления запросов в OpenRouter
* Наследование от `BaseModelWorker` для создания прокси-воркера
* Формирование запросов к `https://openrouter.ai/v1/chat/completions`
* Подстановка модели из `OR_DEFAULT_MODEL` или из оригинального запроса
* Потоковая передача ответа обратно в FastChat с параллельным логированием

### 3. Логирование
* Текстовый лог-файл `logs/traffic.log` в формате CSV или TSV
* Опциональное использование SQLite для расширенного аудита
* Метрики Prometheus `/metrics` для отслеживания:
  - Количества запросов
  - Количества токенов
  - Задержек

### 4. Технический стек
* Python ≥ 3.11
* FastChat ≥ 0.2.24
* httpx для асинхронного проксирования в OpenRouter
* SQLModel + SQLite (опционально) для журнала запросов
* Prometheus client для метрик
* Docker для кроссплатформенного развертывания

### 5. Конфигурация через переменные окружения
| ENV                | По умолчанию       | Описание                                      |
| ------------------ | ------------------ | --------------------------------------------- |
| `OR_HOST`          | `0.0.0.0`          | Хост API-сервера                              |
| `OR_PORT`          | `8000`             | Порт API-сервера                              |
| `OR_API_KEY`       | — **обязательно**  | Ключ OpenRouter                               |
| `OR_DEFAULT_MODEL` | `openai/gpt-4o`    | Модель по умолчанию для запросов к `orcestator` |
| `OR_LOG_FILE`      | `logs/traffic.log` | Путь к текстовому логу                        |
| `OR_DB_PATH`       | пусто → без SQLite | Если указан — используется SQLite             |
| `OR_LOG_LEVEL`     | `info`             | Уровень логирования                           |

### 6. Структура проекта
```
orcestator/
├─ orcestator/
│  ├─ __init__.py
│  ├─ config.py            # чтение ENV
│  ├─ db.py                # модели SQLModel (если OR_DB_PATH)
│  ├─ logger.py            # init logging + Prometheus
│  ├─ proxy_worker.py      # кастомный FastChat-воркер
│  ├─ controller_patch.py  # (опционально) расширение Controller
│  └─ api_server.py        # обёртка запуска openai_api_server
├─ Dockerfile
└─ pyproject.toml
```

### 7. Запуск компонентов
```bash
# контроллер
python -m fastchat.serve.controller --host 0.0.0.0 --port 21001 &
# кастомный воркер-прокси
python -m orcestator.proxy_worker \
       --model-id orcestator \
       --controller http://localhost:21001 \
       --port 8002 &
# OpenAI-API сервер
python -m orcestator.api_server --host $OR_HOST --port $OR_PORT
```

### 8. Dockerfile
```
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["bash", "-c", \
 "python -m fastchat.serve.controller --host 0.0.0.0 --port 21001 & \
  python -m orcestator.proxy_worker --model-id orcestator \
         --controller http://localhost:21001 --port 8002 & \
  python -m orcestator.api_server --host 0.0.0.0 --port 8000"]
```

### 9. Настройка VS Code Copilot
```jsonc
{
  // settings.json
  "openai.apiBaseUrl": "http://localhost:8000/v1",
  "openai.apiKey": "test",           // Copilot принимает любой текст
  "github.copilot.enableAdvancedChat": true
}
```

## Требуемые артефакты

1. **Полный код проекта** согласно структуре выше
2. **INSTALL_win11_no_docker.md** — пошаговая инструкция по установке для Windows 11 без Docker:
   * Установка Python 3.11 x64
   * Установка Git for Windows
   * Установка Poetry
   * Шаги в PowerShell для запуска Orcestator
   * Настройка Copilot
3. **INSTALL_docker.md** — пошаговая инструкция по установке для Windows 11 с Docker:
   * Установка Docker Desktop + WSL2
   * Сборка и запуск контейнера
   * Проверка работы с Copilot

## Правила генерации

1. Общение и документация — **по-русски**
2. Комментарии в коде — **на английском**
3. Код выдаётся только по команде **«Пиши код Orcestator»**
4. Код должен соответствовать PEP 8, быть модульным и читабельным
5. Логи должны быть понятны человеку: `ISO-timestamp | user | assistant | ptok | ctok | latency_ms`
