import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Проверка токена
if not BOT_TOKEN:
    raise ValueError('Токен бота не найден! Проверьте файл .env')
