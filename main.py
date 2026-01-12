import logging
import sys

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Весь ваш текущий код бота здесь
    # ...
    logger.info("Бот успешно запущен")
except Exception as e:
    logger.error(f"Ошибка при запуске бота: {e}")
    sys.exit(1)
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Товары пекарни "Эдем"
PRODUCTS = {
    1: {"name": "Круассан с шоколадом", "price": 120, "emoji": "🥐"},
    2: {"name": "Торт 'Медовик'", "price": 1200, "emoji": "🎂"},
    3: {"name": "Бородинский хлеб", "price": 150, "emoji": "🍞"},
    4: {"name": "Капучино", "price": 180, "emoji": "☕️"},
    5: {"name": "Пирожок с вишней", "price": 85, "emoji": "🥟"},
    6: {"name": "Чизкейк Нью-Йорк", "price": 850, "emoji": "🍰"}
}

# Главное меню
def main_menu():
    keyboard = [
        [KeyboardButton("🍰 Каталог"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("ℹ️ О нас"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """✨ *Добро пожаловать в пекарню "Эдем"!* ✨

🍞 Свежая выпечка каждый день
🎂 Авторские торты на заказ
🥐 Ароматный кофе и десерты

*Выберите действие:*"""
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode='Markdown')

# Показать каталог
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*🍰 Каталог:*\n\nВыберите товар:"
    keyboard = []
    
    for pid, product in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(
            f"{product['emoji']} {product['name']} - {product['price']} ₽",
            callback_data=f"view_{pid}"
        )])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# Показать корзину
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get('cart', {})
    
    if not cart:
        await update.message.reply_text("🛒 *Корзина пуста*", parse_mode='Markdown')
        return
    
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    
    for pid, qty in cart.items():
        product = PRODUCTS[int(pid)]
        cost = product['price'] * qty
        total += cost
        text += f"• {product['emoji']} {product['name']} - {qty} шт. = {cost} ₽\n"
    
    text += f"\n*Итого: {total} ₽*"
    await update.message.reply_text(text, parse_mode='Markdown')

# О пекарне
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """*🍞 Пекарня "Эдем"*

Мы создаем вкусные воспоминания!

*Часы работы:*
Пн-Пт: 7:00 - 22:00
Сб-Вс: 8:00 - 23:00"""
    await update.message.reply_text(text, parse_mode='Markdown')

# Контакты
async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """*📍 Контакты:*

*Адрес:* ул. Пекарская, 15
*Телефон:* +7 (999) 123-45-67
*Email:* edem@bakery.ru"""
    await update.message.reply_text(text, parse_mode='Markdown')

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("view_"):
        pid = int(data.split("_")[1])
        product = PRODUCTS[pid]
        
        text = f"""*{product['emoji']} {product['name']}*

*Цена:* {product['price']} ₽

Добавить в корзину?"""
        
        keyboard = [[
            InlineKeyboardButton("➕ В корзину", callback_data=f"add_{pid}"),
            InlineKeyboardButton("🔙 Назад", callback_data="back")
        ]]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data.startswith("add_"):
        pid = data.split("_")[1]
        
        if 'cart' not in context.user_data:
            context.user_data['cart'] = {}
        
        context.user_data['cart'][pid] = context.user_data['cart'].get(pid, 0) + 1
        
        product = PRODUCTS[int(pid)]
        await query.answer(f"✅ {product['name']} добавлен в корзину!")

# Главная функция
def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("contacts", contacts))
    
    # Кнопки меню
    application.add_handler(MessageHandler(filters.Regex('^🍰 Каталог$'), show_catalog))
    application.add_handler(MessageHandler(filters.Regex('^🛒 Корзина$'), show_cart))
    application.add_handler(MessageHandler(filters.Regex('^ℹ️ О нас$'), about))
    application.add_handler(MessageHandler(filters.Regex('^📞 Контакты$'), contacts))
    
    # Инлайн-кнопки
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("Бот пекарни 'Эдем' запущен...")
    application.run_polling()

if __name__ == '__main__':
    
