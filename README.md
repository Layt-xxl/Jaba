# Telegram‑бот, ДОБЖЕЗДРАВ, команды Жаба

## Установка
Склонируйте репозиторий в отдельную папку и перейдите в нее

Токен бота получается через [@BotFather](t.me/BotFather), нажимаете на newbot, далее действуете по инструкции, в конце вам выдадут токен бота который вы указываете при установке

## Установка используя uv
скачать uv используя команду в powershell 
```pwsh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
или же через через pip
```pwsh
pip install pip
```
после этого мы заходим в папку и прописываем
```pwsh
uv sync
```
и запускаем 
```pwsh
uv run main.py
```

## Запуск через Docker
Запуск происходит через [Docker](docker.com), установить можно на сайте.
После установки в консоли введите следующие команды
```shell
# сборка
docker build -t skinbot .

# запуск (веса монтируются томом, токен через ENV)
docker run -d \
  -e BOT_TOKEN=123456:ABC... \
  -e MODEL_PATH=/weights/best.pt \ # веса уже установлены, можно не менять 
  --name skinbot \
  skinbot

```