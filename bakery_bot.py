from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8568435410:AAEv5CfuyCj6oklglGkKJd-uke4QskivP-w"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = ReplyKeyboardMarkup([
        ["🍰 Каталог", "🛒 Корзина"],
        ["ℹ️ О нас", "📞 Контакты"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "✨ Пекарня 'Эдем' ✨\n\nВыберите действие:",
        reply_markup=menu
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🥐 Круассан - 120₽\n🎂 Торт - 1200₽\n🍞 Хлеб - 150₽")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Пекарня 'Эдем'\nЧасы: 7:00-22:00")

async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📞 ул. Пекарская, 15\n+7 (999) 123-45-67")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), catalog))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ О нас$"), about))
    app.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts))
    print("✅ Бот пекарни 'Эдем' запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
