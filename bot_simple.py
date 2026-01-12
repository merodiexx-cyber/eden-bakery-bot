import logging
from telegram.ext import Application, CommandHandler

# Вставьте свой токен прямо здесь (скопируйте из .env)
TOKEN = '8568435410:AAEv5CfuyCj6oklglGkKJd-uke4QskivP-w'

print('=' * 60)
print('🚀 ЗАПУСК ПРОСТОГО БОТА')
print('=' * 60)
print(f'Токен: {TOKEN[:10]}...')

async def start(update, context):
    await update.message.reply_text('✅ Бот пекарни \"Эдем\" работает!')

def main():
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        
        print('✅ Бот запущен!')
        print('📱 Откройте Telegram и напишите /start')
        print('=' * 60)
        
        app.run_polling()
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == '__main__':
    main()
