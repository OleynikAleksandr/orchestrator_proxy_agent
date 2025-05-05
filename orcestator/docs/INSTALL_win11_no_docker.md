# Установка Orcestator на Windows 11 без Docker

Это пошаговая инструкция по установке и запуску Orcestator на Windows 11 без использования Docker. Следуйте инструкциям ниже, чтобы настроить все необходимые компоненты.

## 1. Установка Python 3.11

1. Перейдите на официальный сайт Python: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Найдите и скачайте Python 3.11 (64-bit) Windows installer
3. Запустите скачанный файл (например, `python-3.11.x-amd64.exe`)
4. **Важно**: Отметьте галочку "Add Python 3.11 to PATH"
5. Выберите "Install Now" для стандартной установки
6. Дождитесь завершения установки и нажмите "Close"

## 2. Установка Git for Windows

1. Перейдите на официальный сайт Git: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Скачайте 64-битную версию Git для Windows
3. Запустите скачанный файл (например, `Git-2.xx.x-64-bit.exe`)
4. Нажимайте "Next" для всех настроек по умолчанию
5. На экране "Adjusting your PATH environment" выберите "Git from the command line and also from 3rd-party software"
6. Продолжайте установку с настройками по умолчанию
7. Нажмите "Install" и дождитесь завершения установки
8. Нажмите "Finish" для завершения установки

## 3. Установка Poetry

1. Откройте PowerShell от имени администратора:
   - Нажмите правой кнопкой мыши на кнопку "Пуск"
   - Выберите "Windows PowerShell (Администратор)"
   - Нажмите "Да" в диалоговом окне контроля учетных записей

2. Выполните следующую команду для установки Poetry:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

3. Закройте и снова откройте PowerShell, чтобы обновить переменные среды

4. Проверьте установку Poetry, выполнив:
   ```powershell
   poetry --version
   ```

## 4. Скачивание и настройка Orcestator

1. Создайте папку для проекта:
   ```powershell
   mkdir C:\Orcestator
   cd C:\Orcestator
   ```

2. Клонируйте репозиторий:
   ```powershell
   git clone https://github.com/OleynikAleksandr/orchestrator_proxy_agent.git .
   ```

3. Перейдите в папку с проектом:
   ```powershell
   cd C:\Orcestator\orcestator
   ```

4. Установите зависимости с помощью Poetry:
   ```powershell
   poetry install
   ```

5. Создайте файл `.env` в папке `C:\Orcestator\orcestator` со следующим содержимым:
   ```
   OR_HOST=0.0.0.0
   OR_PORT=8000
   OR_API_KEY=ваш_ключ_openrouter  # Замените на ваш ключ OpenRouter
   OR_DEFAULT_MODEL=openai/gpt-4o
   OR_LOG_FILE=logs/traffic.log
   OR_LOG_LEVEL=info
   ```

   **Важно**: Замените `ваш_ключ_openrouter` на ваш реальный ключ API от [OpenRouter](https://openrouter.ai/).

## 5. Запуск Orcestator

1. Откройте PowerShell и перейдите в папку проекта:
   ```powershell
   cd C:\Orcestator\orcestator
   ```

2. Запустите контроллер FastChat:
   ```powershell
   Start-Process powershell -ArgumentList "poetry run python -m fastchat.serve.controller --host 0.0.0.0 --port 21001"
   ```

3. Подождите 5-10 секунд, затем запустите прокси-воркер:
   ```powershell
   Start-Process powershell -ArgumentList "poetry run python -m orcestator.proxy_worker --model-id orcestator --controller http://localhost:21001 --port 8002"
   ```

4. Подождите 5-10 секунд, затем запустите API-сервер:
   ```powershell
   poetry run python -m orcestator.api_server --host 0.0.0.0 --port 8000
   ```

5. Проверьте, что сервер запущен, открыв в браузере адрес:
   ```
   http://localhost:8000/v1/models
   ```
   
   Вы должны увидеть JSON-ответ, содержащий модель "orcestator".

## 6. Настройка VS Code Copilot

1. Установите VS Code, если он еще не установлен: [https://code.visualstudio.com/download](https://code.visualstudio.com/download)

2. Установите расширение GitHub Copilot:
   - Откройте VS Code
   - Перейдите во вкладку Extensions (Ctrl+Shift+X)
   - Найдите "GitHub Copilot" и установите его
   - Войдите в свою учетную запись GitHub, если потребуется

3. Настройте Copilot для работы с Orcestator:
   - Откройте настройки VS Code (File > Preferences > Settings или Ctrl+,)
   - Нажмите на значок {} в правом верхнем углу для редактирования settings.json
   - Добавьте следующие строки:
     ```json
     "openai.apiBaseUrl": "http://localhost:8000/v1",
     "openai.apiKey": "test",
     "github.copilot.enableAdvancedChat": true
     ```
   - Сохраните файл (Ctrl+S)

4. Перезапустите VS Code

5. Проверьте работу Copilot:
   - Откройте Copilot Chat (Ctrl+Shift+I)
   - Выберите режим "Agent"
   - Задайте вопрос и проверьте, что получаете ответ

## Устранение неполадок

### Если Copilot не подключается к Orcestator:

1. Убедитесь, что все три компонента (контроллер, воркер и API-сервер) запущены
2. Проверьте, что в файле `.env` указан правильный ключ API OpenRouter
3. Проверьте доступность API по адресу http://localhost:8000/v1/models
4. Проверьте логи в папке `logs` для выявления ошибок

### Если возникают ошибки при установке зависимостей:

1. Убедитесь, что у вас установлена правильная версия Python (3.11)
2. Попробуйте обновить pip:
   ```powershell
   python -m pip install --upgrade pip
   ```
3. Попробуйте обновить Poetry:
   ```powershell
   poetry self update
   ```

### Если порты заняты:

Измените порты в файле `.env` и соответствующих командах запуска, если стандартные порты (8000, 21001, 8002) уже используются другими приложениями.
