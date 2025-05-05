# Установка Orcestator на Windows 11 с Docker

Это пошаговая инструкция по установке и запуску Orcestator на Windows 11 с использованием Docker Desktop. Следуйте инструкциям ниже, чтобы настроить все необходимые компоненты.

## 1. Установка Docker Desktop и WSL2

### Установка WSL2

1. Откройте PowerShell от имени администратора:
   - Нажмите правой кнопкой мыши на кнопку "Пуск"
   - Выберите "Windows PowerShell (Администратор)"
   - Нажмите "Да" в диалоговом окне контроля учетных записей

2. Установите WSL2, выполнив команду:
   ```powershell
   wsl --install
   ```

3. Перезагрузите компьютер после завершения установки

4. После перезагрузки автоматически запустится установка Ubuntu. Создайте имя пользователя и пароль, когда будет предложено.

### Установка Docker Desktop

1. Перейдите на официальный сайт Docker: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

2. Нажмите кнопку "Download for Windows" и скачайте установщик Docker Desktop

3. Запустите скачанный файл (например, `Docker Desktop Installer.exe`)

4. Следуйте инструкциям установщика:
   - Убедитесь, что опция "Use WSL 2 instead of Hyper-V" включена
   - Нажмите "Ok" для продолжения установки

5. После завершения установки нажмите "Close and restart" для перезагрузки компьютера

6. После перезагрузки Docker Desktop запустится автоматически. Если этого не произошло, запустите его вручную через меню "Пуск"

7. При первом запуске Docker Desktop может попросить принять условия лицензии. Примите их, чтобы продолжить.

8. Дождитесь, пока Docker Desktop полностью загрузится (значок в трее станет неподвижным)

## 2. Скачивание и сборка Orcestator

1. Установите Git, если он еще не установлен:
   - Перейдите на [https://git-scm.com/download/win](https://git-scm.com/download/win)
   - Скачайте и установите 64-битную версию Git для Windows
   - Используйте настройки по умолчанию при установке

2. Откройте PowerShell (не требуются права администратора):
   - Нажмите правой кнопкой мыши на кнопку "Пуск"
   - Выберите "Windows PowerShell"

3. Создайте папку для проекта:
   ```powershell
   mkdir C:\Orcestator
   cd C:\Orcestator
   ```

4. Клонируйте репозиторий:
   ```powershell
   git clone https://github.com/OleynikAleksandr/orchestrator_proxy_agent.git .
   ```

5. Перейдите в папку с проектом:
   ```powershell
   cd C:\Orcestator\orcestator
   ```

6. Создайте файл `.env` в папке `C:\Orcestator\orcestator` со следующим содержимым:
   ```
   OR_HOST=0.0.0.0
   OR_PORT=8000
   OR_API_KEY=ваш_ключ_openrouter  # Замените на ваш ключ OpenRouter
   OR_DEFAULT_MODEL=openai/gpt-4o
   OR_LOG_FILE=logs/traffic.log
   OR_LOG_LEVEL=info
   ```

   **Важно**: Замените `ваш_ключ_openrouter` на ваш реальный ключ API от [OpenRouter](https://openrouter.ai/).

7. Соберите Docker-образ:
   ```powershell
   docker build -t orcestator .
   ```

   Этот процесс может занять несколько минут, так как Docker будет скачивать базовый образ Python и устанавливать все зависимости.

## 3. Запуск Orcestator в Docker

1. Запустите контейнер с Orcestator:
   ```powershell
   docker run -d --name orcestator -p 8000:8000 -p 8001:8001 --env-file .env orcestator
   ```

   Эта команда:
   - Запускает контейнер в фоновом режиме (`-d`)
   - Называет контейнер "orcestator" (`--name orcestator`)
   - Пробрасывает порты 8000 и 8001 из контейнера на хост (`-p 8000:8000 -p 8001:8001`)
   - Передает переменные окружения из файла `.env` (`--env-file .env`)
   - Использует образ "orcestator", который мы только что собрали

2. Проверьте, что контейнер запущен:
   ```powershell
   docker ps
   ```

   Вы должны увидеть контейнер "orcestator" в списке запущенных контейнеров.

3. Проверьте логи контейнера:
   ```powershell
   docker logs orcestator
   ```

   Вы должны увидеть сообщения о запуске контроллера, воркера и API-сервера.

4. Проверьте, что API-сервер работает, открыв в браузере адрес:
   ```
   http://localhost:8000/v1/models
   ```
   
   Вы должны увидеть JSON-ответ, содержащий модель "orcestator".

## 4. Настройка VS Code Copilot

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

## 5. Управление контейнером

### Остановка контейнера

```powershell
docker stop orcestator
```

### Запуск остановленного контейнера

```powershell
docker start orcestator
```

### Удаление контейнера

```powershell
docker rm -f orcestator
```

### Просмотр логов

```powershell
docker logs orcestator
```

Для постоянного отслеживания логов в реальном времени:

```powershell
docker logs -f orcestator
```

## Устранение неполадок

### Если контейнер не запускается:

1. Проверьте логи контейнера:
   ```powershell
   docker logs orcestator
   ```

2. Убедитесь, что в файле `.env` указан правильный ключ API OpenRouter

3. Проверьте, что порты 8000 и 8001 не заняты другими приложениями:
   ```powershell
   netstat -ano | findstr :8000
   netstat -ano | findstr :8001
   ```

   Если порты заняты, измените порты в команде запуска контейнера:
   ```powershell
   docker run -d --name orcestator -p 8080:8000 -p 8081:8001 --env-file .env orcestator
   ```
   
   И соответственно обновите настройки в VS Code:
   ```json
   "openai.apiBaseUrl": "http://localhost:8080/v1",
   ```

### Если Docker Desktop не запускается:

1. Убедитесь, что WSL2 установлен и работает:
   ```powershell
   wsl --status
   ```

2. Проверьте, что виртуализация включена в BIOS/UEFI вашего компьютера

3. Перезапустите службу Docker:
   ```powershell
   net stop com.docker.service
   net start com.docker.service
   ```

### Если Copilot не подключается к Orcestator:

1. Убедитесь, что контейнер запущен и API-сервер доступен по адресу http://localhost:8000/v1/models
2. Проверьте настройки VS Code
3. Перезапустите VS Code
