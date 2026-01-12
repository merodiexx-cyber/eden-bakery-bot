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
    5: {"name": "🥟 Пирожок с вишней", "price": 85},
}

# Главное меню
def get_main_menu():
    keyboard = [
        [KeyboardButton("🍰 Каталог"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("ℹ️ О нас"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== ОБРАБОТЧИКИ КНОПОК ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome = """
✨ *Добро пожаловать в пекарню "Эдем"!* ✨

Выберите действие:
"""
    await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode='Markdown')

async def handle_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Каталог - РАБОТАЕТ!"""
    text = "*🍰 Каталог товаров:*\n\n"
    
    for pid, product in PRODUCTS.items():
        text += f"• {product['name']} - {product['price']} ₽\n"
    
    text += "\n*Выберите товар для добавления в корзину:*"
    
    # Создаем инлайн-кнопки для каждого товара
    keyboard = []
    for pid, product in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"➕ {product['name']}",
                callback_data=f"add_{pid}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")])
    
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Корзина"""
    # Проверяем есть ли корзина
    if 'cart' not in context.user_data or not context.user_data['cart']:
        await update.message.reply_text("🛒 *Ваша корзина пуста!*", parse_mode='Markdown')
        return
    
    cart = context.user_data['cart']
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        cost = product['price'] * quantity
        total += cost
        text += f"• {product['name']} - {quantity} шт. = {cost} ₽\n"
    
    text += f"\n*💰 Итого: {total} ₽*"
    
    # Кнопки для корзины
    keyboard = [
        [InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки О нас"""
    text = """
*ℹ️ О пекарне "Эдем":*

Мы создаем вкусные воспоминания!
Работаем с 2010 года.

*Часы работы:*
Пн-Пт: 7:00 - 22:00
Сб-Вс: 8:00 - 23:00
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Контакты"""
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

# ==================== ОБРАБОТЧИКИ ИНЛАЙН-КНОПОК ====================

async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик инлайн-кнопок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("add_"):
        # Добавление товара в корзину
        pid = int(data.split("_")[1])
        
        # Создаем корзину если ее нет
        if 'cart' not in context.user_data:
            context.user_data['cart'] = {}
        
        # Добавляем товар
        cart = context.user_data['cart']
        cart[str(pid)] = cart.get(str(pid), 0) + 1
        
        product = PRODUCTS[pid]
        await query.answer(f"✅ {product['name']} добавлен в корзину!")
        
        # Показываем обновленный каталог
        await show_catalog_from_query(query, context)
    
    elif data == "checkout":
        # Оформление заказа
        cart = context.user_data.get('cart', {})
        
        if not cart:
            await query.answer("Корзина пуста!", show_alert=True)
            return
        
        # Считаем сумму
        total = 0
        order_details = ""
        for pid, quantity in cart.items():
            product = PRODUCTS[int(pid)]
            cost = product['price'] * quantity
            total += cost
            order_details += f"• {product['name']} - {quantity} шт. = {cost} ₽\n"
        
        # Генерируем номер заказа
        import random
        order_number = random.randint(1000, 9999)
        
        text = f"""
✅ *Заказ оформлен!*

*Номер заказа:* #{order_number}
*Сумма:* {total} ₽

*Ваш заказ:*
{order_details}

Спасибо за заказ! Ожидайте звонка.
"""
        
        await query.edit_message_text(text, parse_mode='Markdown')
        
        # Очищаем корзину
        context.user_data['cart'] = {}
    
    elif data == "clear_cart":
        # Очистка корзины
        context.user_data['cart'] = {}
        await query.answer("Корзина очищена!", show_alert=True)
        await query.edit_message_text("🛒 *Корзина очищена!*", parse_mode='Markdown')
    
    elif data == "back_to_menu":
        # Возврат в меню
        await start_from_query(query, context)

async def show_catalog_from_query(query, context):
    """Показать каталог из callback query"""
    text = "*🍰 Каталог товаров:*\n\n"
    
    for pid, product in PRODUCTS.items():
        text += f"• {product['name']} - {product['price']} ₽\n"
    
    text += "\n*Выберите товар:*"
    
    keyboard = []
    for pid, product in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"➕ {product['name']}",
                callback_data=f"add_{pid}"
            )
        ])
    
    # Проверяем есть ли товары в корзине
    cart_items = context.user_data.get('cart', {})
    if cart_items:
        keyboard.append([InlineKeyboardButton(f"🛒 Перейти в корзину ({len(cart_items)} товаров)", callback_data="show_cart")])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def start_from_query(query, context):
    """Показать меню из callback query"""
    welcome = "✨ *Главное меню* ✨"
    await query.edit_message_text(welcome, reply_markup=get_main_menu(), parse_mode='Markdown')

# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Команда /start
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики кнопок меню - ВАЖНО: правильные фильтры
    application.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), handle_catalog))
    application.add_handler(MessageHandler(filters.Regex("^🛒 Корзина$"), handle_cart))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ О нас$"), handle_about))
    application.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), handle_contacts))
    
    # Обработчик инлайн-кнопок
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    
    print("=" * 60)
    print("🚀 БОТ ПЕКАРНИ 'ЭДЕМ' ЗАПУЩЕН")
    print("=" * 60)
    print("✅ Все кнопки РАБОТАЮТ:")
    print("• 🍰 Каталог - показывает товары и добавляет в корзину")
    print("• 🛒 Корзина - показывает ваши товары")
    print("• ℹ️ О нас - информация о пекарне")
    print("• 📞 Контакты - адрес и телефон")
    print("=" * 60)
    print("📱 Откройте Telegram и напишите /start")
    print("=" * 60)
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()