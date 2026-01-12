from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Токен бота
TOKEN = "8568435410:AAEv5CfuyCj6oklglGkKJd-uke4QskivP-w"

# Товары
PRODUCTS = {
    1: {"name": "🥐 Круассан", "price": 120},
    2: {"name": "🎂 Торт", "price": 1200},
    3: {"name": "🍞 Хлеб", "price": 150},
}

# Главное меню
def get_main_menu():
    return ReplyKeyboardMarkup([
        ["🍰 Каталог", "🛒 Корзина"],
        ["ℹ️ О нас", "📞 Контакты"]
    ], resize_keyboard=True)

# ==================== ОБРАБОТЧИКИ ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    text = "✨ *Пекарня 'Эдем'* ✨\n\nВыберите действие:"
    await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode='Markdown')

async def handle_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка Каталог"""
    text = "*🍰 Каталог товаров:*\n\n"
    
    for pid, product in PRODUCTS.items():
        text += f"• {product['name']} - {product['price']} ₽\n"
    
    text += "\n*Добавить в корзину:*"
    
    # Создаем кнопки
    keyboard = [
        [InlineKeyboardButton("➕ Круассан", callback_data="add_1")],
        [InlineKeyboardButton("➕ Торт", callback_data="add_2")],
        [InlineKeyboardButton("➕ Хлеб", callback_data="add_3")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка Корзина"""
    # Проверяем корзину
    cart = context.user_data.get('cart', {})
    
    if not cart:
        await update.message.reply_text("🛒 *Корзина пуста*", parse_mode='Markdown')
        return
    
    text = "🛒 *Ваша корзина:*\n\n"
    total = 0
    
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        cost = product['price'] * quantity
        total += cost
        text += f"• {product['name']} - {quantity} шт. = {cost} ₽\n"
    
    text += f"\n*💰 Итого: {total} ₽*"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка О нас"""
    text = "ℹ️ *О пекарне:*\n\nМы работаем с 2010 года!\nЧасы: 7:00-22:00"
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка Контакты"""
    text = "📞 *Контакты:*\n\nул. Пекарская, 15\n+7 (999) 123-45-67"
    await update.message.reply_text(text, parse_mode='Markdown')

# Обработка инлайн-кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("add_"):
        pid = data.split("_")[1]
        
        # Создаем корзину
        if 'cart' not in context.user_data:
            context.user_data['cart'] = {}
        
        # Добавляем товар
        cart = context.user_data['cart']
        cart[pid] = cart.get(pid, 0) + 1
        
        product = PRODUCTS[int(pid)]
        await query.answer(f"✅ {product['name']} добавлен!")
        
        # Показываем обновленный каталог
        text = f"✅ *{product['name']} добавлен в корзину!*\n\n"
        text += "*Каталог:*\n"
        for pid, product in PRODUCTS.items():
            text += f"• {product['name']} - {product['price']} ₽\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ Круассан", callback_data="add_1")],
            [InlineKeyboardButton("➕ Торт", callback_data="add_2")],
            [InlineKeyboardButton("➕ Хлеб", callback_data="add_3")],
            [InlineKeyboardButton("🛒 Корзина", callback_data="show_cart")],
            [InlineKeyboardButton("🔙 Меню", callback_data="back")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "show_cart":
        cart = context.user_data.get('cart', {})
        
        if not cart:
            text = "🛒 *Корзина пуста*"
        else:
            text = "🛒 *Ваша корзина:*\n\n"
            total = 0
            
            for pid, quantity in cart.items():
                product = PRODUCTS[int(pid)]
                cost = product['price'] * quantity
                total += cost
                text += f"• {product['name']} - {quantity} шт. = {cost} ₽\n"
            
            text += f"\n*💰 Итого: {total} ₽*"
        
        keyboard = [[InlineKeyboardButton("🔙 Каталог", callback_data="back_catalog")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data == "back":
        text = "✨ *Главное меню* ✨"
        await query.edit_message_text(text, reply_markup=get_main_menu(), parse_mode='Markdown')
    
    elif data == "back_catalog":
        text = "*🍰 Каталог товаров:*\n\n"
        for pid, product in PRODUCTS.items():
            text += f"• {product['name']} - {product['price']} ₽\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ Круассан", callback_data="add_1")],
            [InlineKeyboardButton("➕ Торт", callback_data="add_2")],
            [InlineKeyboardButton("➕ Хлеб", callback_data="add_3")],
            [InlineKeyboardButton("🔙 Меню", callback_data="back")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# Главная функция
def main():
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    
    # Кнопки меню
    app.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), handle_catalog))
    app.add_handler(MessageHandler(filters.Regex("^🛒 Корзина$"), handle_cart))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ О нас$"), handle_about))
    app.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), handle_contacts))
    
    # Инлайн-кнопки
    app.add_handler(CallbackQueryHandler(handle_buttons))
    
    print("=" * 50)
    print("✅ БОТ ЗАПУЩЕН!")
    print("=" * 50)
    print("ВСЕ КНОПКИ РАБОТАЮТ:")
    print("• 🍰 Каталог - показывает товары")
    print("• 🛒 Корзина - показывает корзину")
    print("• ℹ️ О нас - информация")
    print("• 📞 Контакты - адрес и телефон")
    print("=" * 50)
    print("📱 Откройте Telegram и напишите /start")
    print("=" * 50)
    
    # Запускаем
    app.run_polling()

if __name__ == "__main__":
    main()
    