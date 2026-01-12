import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8568435410:AAEv5CfuyCj6oklglGkKJd-uke4QskivP-w"

# Товары пекарни
PRODUCTS = {
    1: {"name": "🥐 Круассан с шоколадом", "price": 120},
    2: {"name": "🎂 Торт 'Медовик'", "price": 1200},
    3: {"name": "🍞 Бородинский хлеб", "price": 150},
    4: {"name": "☕️ Капучино", "price": 180},
}

# Главное меню
def get_main_menu():
    keyboard = [
        [KeyboardButton("🍰 Каталог"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("ℹ️ О нас"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== КОМАНДЫ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome = """
✨ *Добро пожаловать в пекарню "Эдем"!* ✨

🍞 Свежая выпечка каждый день
🎂 Авторские торты на заказ
🥐 Ароматный кофе и десерты

*Выберите действие в меню ниже:*
"""
    await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode='Markdown')

async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Каталог"""
    text = "*🍰 Каталог товаров:*\n\n"
    
    for pid, product in PRODUCTS.items():
        text += f"• {product['name']} - {product['price']} ₽\n"
    
    # Кнопки для добавления в корзину
    keyboard = []
    for pid in PRODUCTS:
        keyboard.append([InlineKeyboardButton(
            f"➕ Добавить {PRODUCTS[pid]['name'][:10]}",
            callback_data=f"add_{pid}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 В меню", callback_data="back_menu")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Корзина"""
    if 'cart' not in context.user_data or not context.user_data['cart']:
        text = "🛒 *Ваша корзина пуста*\n\nДобавьте товары из каталога!"
        await update.message.reply_text(text, parse_mode='Markdown')
        return
    
    cart = context.user_data['cart']
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        item_total = product['price'] * quantity
        total += item_total
        text += f"• {product['name']} - {quantity} шт. × {product['price']} ₽ = {item_total} ₽\n"
    
    text += f"\n*💰 Итого: {total} ₽*"
    
    keyboard = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_menu")]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки О нас"""
    text = """
*🍞 Пекарня "Эдем"*

Мы создаем вкусные воспоминания!

*Часы работы:*
Пн-Пт: 7:00 - 22:00
Сб-Вс: 8:00 - 23:00
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def contacts_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Контакты - ИСПРАВЛЕНО"""
    text = """
*📞 Наши контакты:*

*Адрес:* ул. Пекарская, 15
*Телефон:* +7 (999) 123-45-67
*Email:* edem@bakery.ru

*Как добраться:*
🚇 Метро "Пекарская"
🚌 Автобусы: 15, 47, 89
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== ИНЛАЙН-КНОПКИ ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("add_"):
        pid = data.split("_")[1]
        
        # Инициализируем корзину
        if 'cart' not in context.user_data:
            context.user_data['cart'] = {}
        
        cart = context.user_data['cart']
        cart[pid] = cart.get(pid, 0) + 1
        
        product = PRODUCTS[int(pid)]
        await query.answer(f"✅ {product['name']} добавлен в корзину!")
        
        # Показываем обновленный каталог
        text = "*✅ Товар добавлен!*\n\n*Каталог товаров:*\n\n"
        for pid, product in PRODUCTS.items():
            text += f"• {product['name']} - {product['price']} ₽\n"
        
        keyboard = []
        for pid in PRODUCTS:
            keyboard.append([InlineKeyboardButton(
                f"➕ Добавить {PRODUCTS[pid]['name'][:10]}",
                callback_data=f"add_{pid}"
            )])
        
        keyboard.append([InlineKeyboardButton("🛒 Перейти в корзину", callback_data="show_cart")])
        keyboard.append([InlineKeyboardButton("🔙 В меню", callback_data="back_menu")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "checkout":
        cart = context.user_data.get('cart', {})
        
        if not cart:
            await query.answer("Корзина пуста!", show_alert=True)
            return
        
        total = 0
        for pid, quantity in cart.items():
            product = PRODUCTS[int(pid)]
            total += product['price'] * quantity
        
        text = f"""
✅ *Заказ оформлен!*

*Номер заказа:* #{hash(str(cart)) % 10000}
*Сумма:* {total} ₽

Спасибо за заказ! Ожидайте звонка.
"""
        
        await query.edit_message_text(text, parse_mode='Markdown')
        context.user_data['cart'] = {}
    
    elif data == "show_cart":
        await show_cart_from_query(query, context)
    
    elif data == "back_menu":
        await start_from_query(query, context)

async def show_cart_from_query(query, context):
    cart = context.user_data.get('cart', {})
    
    if not cart:
        text = "🛒 *Ваша корзина пуста*"
        await query.edit_message_text(text, parse_mode='Markdown')
        return
    
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        item_total = product['price'] * quantity
        total += item_total
        text += f"• {product['name']} - {quantity} шт. × {product['price']} ₽ = {item_total} ₽\n"
    
    text += f"\n*💰 Итого: {total} ₽*"
    
    keyboard = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🔙 В меню", callback_data="back_menu")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start_from_query(query, context):
    welcome = "✨ *Добро пожаловать!* ✨"
    await query.edit_message_text(welcome, reply_markup=get_main_menu(), parse_mode='Markdown')

# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    
    # Обработчики кнопок меню - ВАЖНО: правильные фильтры
    application.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), show_catalog))
    application.add_handler(MessageHandler(filters.Regex("^🛒 Корзина$"), show_cart))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ О нас$"), about_us))
    application.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts_info))  # ИСПРАВЛЕНО
    
    # Инлайн-кнопки
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("=" * 60)
    print("🚀 БОТ ПЕКАРНИ 'ЭДЕМ' ЗАПУЩЕН")
    print("=" * 60)
    print("✅ Все кнопки работают:")
    print("• 🍰 Каталог - показывает товары")
    print("• 🛒 Корзина - показывает корзину")
    print("• ℹ️ О нас - информация о пекарне")
    print("• 📞 Контакты - адрес и телефон")  # Теперь работает!
    print("=" * 60)
    print("📱 Откройте Telegram и напишите /start")
    print("=" * 60)
    
    application.run_polling()

if __name__ == "__main__":
    main()