# 🚀 Запуск YomuBot с LocalTunnel

## 📋 Требования
- Python 3.8+
- Node.js и npm
- Установленный localtunnel: `npm install -g localtunnel`
- Альтернативно: ngrok (более стабильный)

## 🔧 Шаги для запуска

### 1. Запуск API сервера
```bash
cd d:/telelingo/applanguagejapanese-main
python bot.py
```
Сервер запустится на порту 8080

### 2. Запуск туннеля (выберите один вариант)

#### Вариант А: LocalTunnel
```bash
cd d:/telelingo/applanguagejapanese-main
start-localtunnel.bat
```

#### Вариант Б: ngrok (рекомендуется)
```bash
cd d:/telelingo/applanguagejapanese-main
start-ngrok.bat
```

### 3. Обновление адреса в index.html
После запуска туннеля:
- **LocalTunnel:** измените `const API_BASE = 'https://ваш-subdomain.loca.lt'`
- **ngrok:** измените `const API_BASE = 'https://ваш-url.ngrok-free.app'`

### 4. Проверка работы
- API: https://ваш-адрес/api/user
- Web App: откройте через Telegram бота

## 🐛 Частые проблемы

### Проблема: localtunnel не работает (503 Service Unavailable)
**Решение:** Используйте ngrok - он более стабильный

### Проблема: CORS ошибки
**Решение:** В API уже есть CORS middleware

### Проблема: Звуки не работают
**Причина:** HTTPS требуется для аудио в Telegram WebApp
**Решение:** Оба туннеля предоставляют HTTPS

### Проблема: GIF не загружаются
**Причина:** Mixed content (HTTP/HTTPS)
**Решение:** Убедитесь что все URL используют HTTPS

## 🔍 Отладка

Откройте Chrome DevTools в WebApp и проверьте:
1. Console - ошибки JavaScript
2. Network - статус запросов к API
3. Headers - наличие X-Telegram-Init-Data

## 📝 Изменение subdomain
Если subdomain занят, измените в двух местах:
1. `start-localtunnel.bat` --subdomain ваше-имя
2. `index.html` строка `const API_BASE = 'https://ваше-имя.loca.lt'`
