# Orcestator

![Orcestator Logo](https://img.shields.io/badge/Orcestator-Proxy%20Agent-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastChat](https://img.shields.io/badge/FastChat-0.2.24+-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

**Orcestator** — это прокси-оркестратор для языковых моделей с OpenAI-совместимым API, который позволяет использовать различные LLM через единый интерфейс.

## Содержание

- [Обзор](#обзор)
- [Функциональность](#функциональность)
- [Архитектура](#архитектура)
- [Установка](#установка)
  - [Windows 11 без Docker](#windows-11-без-docker)
  - [Windows 11 с Docker](#windows-11-с-docker)
- [Конфигурация](#конфигурация)
- [Использование](#использование)
- [Логирование и мониторинг](#логирование-и-мониторинг)
- [Возможности для развития](#возможности-для-развития)
- [Лицензия](#лицензия)

## Обзор

Orcestator предоставляет OpenAI-совместимый API для доступа к различным языковым моделям через [OpenRouter](https://openrouter.ai/). Это позволяет использовать инструменты, разработанные для OpenAI API (например, VS Code Copilot), с различными моделями, такими как GPT-4o, Claude 3.5 и другими.

Основные преимущества:
- Единый интерфейс для доступа к различным LLM
- Совместимость с инструментами, использующими OpenAI API
- Подробное логирование запросов и ответов
- Метрики для мониторинга использования
- Простая настройка и развертывание

## Функциональность

- **OpenAI-совместимый API**:
  - Поддержка эндпоинтов `/v1/models` и `/v1/chat/completions`
  - Поддержка потоковой передачи данных (streaming)
  - Подмена поля `model` на `"orcestator"` в ответах для совместимости с Copilot

- **Основной движок — FastChat**:
  - Использование штатного `controller` и `openai_api_server`
  - Кастомный воркер-прокси для перенаправления запросов в OpenRouter
  - Наследование от `BaseModelWorker` для создания прокси-воркера

- **Логирование**:
  - Текстовый лог-файл `logs/traffic.log` в формате CSV с разделителем `|`
  - Опциональное использование SQLite для расширенного аудита
  - Метрики Prometheus `/metrics` для отслеживания:
    - Количества запросов
    - Количества токенов
    - Задержек

## Архитектура

Orcestator состоит из трех основных компонентов:

1. **FastChat Controller** — управляет доступными моделями и маршрутизацией запросов
2. **Proxy Worker** — кастомный воркер, который перенаправляет запросы в OpenRouter
3. **OpenAI API Server** — предоставляет OpenAI-совместимый API

Схема работы:
```
Клиент (VS Code Copilot) → OpenAI API Server → Controller → Proxy Worker → OpenRouter → LLM (GPT-4o, Claude и др.)
```

Структура проекта:
```
orcestator/
├─ orcestator/
│  ├─ __init__.py
│  ├─ config.py            # чтение ENV
│  ├─ db.py                # модели SQLModel (если OR_DB_PATH)
│  ├─ logger.py            # init logging + Prometheus
│  ├─ proxy_worker.py      # кастомный FastChat-воркер
│  ├─ controller_patch.py  # расширение Controller
│  └─ api_server.py        # обёртка запуска openai_api_server
├─ docs/
│  ├─ INSTALL_win11_no_docker.md
│  └─ INSTALL_docker.md
├─ Dockerfile
└─ pyproject.toml
```

## Установка

### Windows 11 без Docker

Подробная инструкция по установке на Windows 11 без использования Docker доступна в файле [INSTALL_win11_no_docker.md](orcestator/docs/INSTALL_win11_no_docker.md).

Краткая последовательность действий:
1. Установка Python 3.11 x64
2. Установка Git for Windows
3. Установка Poetry
4. Клонирование репозитория
5. Установка зависимостей
6. Настройка переменных окружения
7. Запуск компонентов
8. Настройка VS Code Copilot

### Windows 11 с Docker

Подробная инструкция по установке на Windows 11 с использованием Docker доступна в файле [INSTALL_docker.md](orcestator/docs/INSTALL_docker.md).

Краткая последовательность действий:
1. Установка Docker Desktop и WSL2
2. Клонирование репозитория
3. Настройка переменных окружения
4. Сборка Docker-образа
5. Запуск контейнера
6. Настройка VS Code Copilot

## Конфигурация

Orcestator настраивается через переменные окружения, которые можно задать в файле `.env`:

| ENV                | По умолчанию       | Описание                                      |
| ------------------ | ------------------ | --------------------------------------------- |
| `OR_HOST`          | `0.0.0.0`          | Хост API-сервера                              |
| `OR_PORT`          | `8000`             | Порт API-сервера                              |
| `OR_API_KEY`       | — **обязательно**  | Ключ OpenRouter                               |
| `OR_DEFAULT_MODEL` | `openai/gpt-4o`    | Модель по умолчанию для запросов к `orcestator` |
| `OR_LOG_FILE`      | `logs/traffic.log` | Путь к текстовому логу                        |
| `OR_DB_PATH`       | пусто → без SQLite | Если указан — используется SQLite             |
| `OR_LOG_LEVEL`     | `info`             | Уровень логирования                           |

## Использование

### Запуск компонентов

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

### Настройка VS Code Copilot

```jsonc
// settings.json
{
  "openai.apiBaseUrl": "http://localhost:8000/v1",
  "openai.apiKey": "test",           // Copilot принимает любой текст
  "github.copilot.enableAdvancedChat": true
}
```

### Проверка работоспособности

Проверить доступность API можно с помощью curl:

```bash
curl http://localhost:8000/v1/models
```

Ответ должен содержать модель "orcestator":

```json
{
  "object": "list",
  "data": [
    {
      "id": "orcestator",
      "object": "model",
      "created": 1677610602,
      "owned_by": "orcestator",
      "permission": [],
      "root": "orcestator",
      "parent": null
    }
  ]
}
```

## Логирование и мониторинг

### Текстовые логи

Логи запросов сохраняются в файл `logs/traffic.log` в формате CSV с разделителем `|`:

```
timestamp | user | assistant | prompt_tokens | completion_tokens | latency_ms | model | original_model
```

### Prometheus метрики

Метрики доступны по адресу `http://localhost:8001/metrics` и включают:

- `orcestator_requests_total` — общее количество запросов
- `orcestator_prompt_tokens_total` — общее количество токенов в запросах
- `orcestator_completion_tokens_total` — общее количество токенов в ответах
- `orcestator_request_latency_seconds` — время обработки запросов
- `orcestator_active_requests` — количество активных запросов

## Возможности для развития

Orcestator можно расширить и улучшить следующими способами:

1. **Поддержка дополнительных эндпоинтов OpenAI API**:
   - `/v1/embeddings` для векторных представлений
   - `/v1/completions` для совместимости с более старыми инструментами
   - `/v1/images/generations` для генерации изображений

2. **Расширение функциональности**:
   - Кэширование ответов для экономии токенов
   - Балансировка нагрузки между несколькими провайдерами LLM
   - Фильтрация и модерация контента
   - Поддержка локальных моделей через FastChat

3. **Улучшение мониторинга и логирования**:
   - Интеграция с Grafana для визуализации метрик
   - Расширенная аналитика использования
   - Алерты при превышении лимитов или ошибках

4. **Безопасность и аутентификация**:
   - Поддержка API ключей для разных пользователей
   - Ограничение доступа по IP
   - Квоты на использование для разных пользователей

5. **Интеграции**:
   - Поддержка других провайдеров LLM помимо OpenRouter
   - Интеграция с инструментами для RAG (Retrieval-Augmented Generation)
   - Поддержка функций (function calling) для инструментов

## Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).
