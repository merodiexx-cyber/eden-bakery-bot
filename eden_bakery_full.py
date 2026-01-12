import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import random
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8568435410:AAEv5CfuyCj6oklglGkKJd-uke4QskivP-w"

# БАЗА ДАННЫХ ТОВАРОВ
PRODUCTS = {
    1: {"name": "🥐 Круассан с шоколадом", "price": 120, "category": "Выпечка", "weight": "80г", "desc": "Свежий круассан с бельгийским шоколадом"},
    2: {"name": "🎂 Торт 'Медовик'", "price": 1200, "category": "Торты", "weight": "1.2кг", "desc": "Классический медовый торт со сметанным кремом"},
    3: {"name": "🍞 Бородинский хлеб", "price": 150, "category": "Хлеб", "weight": "500г", "desc": "Темный хлеб с тмином и кориандром"},
    4: {"name": "☕️ Капучино", "price": 180, "category": "Напитки", "weight": "300мл", "desc": "Кофе с молочной пенкой"},
    5: {"name": "🥟 Пирожок с вишней", "price": 85, "category": "Выпечка", "weight": "100г", "desc": "Домашний пирожок с вишневой начинкой"},
    6: {"name": "🍰 Чизкейк Нью-Йорк", "price": 850, "category": "Десерты", "weight": "800г", "desc": "Нежный чизкейк с ягодным топпингом"},
    7: {"name": "🍪 Печенье овсяное", "price": 65, "category": "Выпечка", "weight": "50г", "desc": "Домашнее овсяное печенье с изюмом"},
    8: {"name": "🥖 Французский багет", "price": 130, "category": "Хлеб", "weight": "250г", "desc": "Хрустящий багет с хрустящей корочкой"},
    9: {"name": "🍩 Пончик с глазурью", "price": 95, "category": "Десерты", "weight": "70г", "desc": "Воздушный пончик с сахарной глазурью"},
    10: {"name": "🍵 Латте", "price": 200, "category": "Напитки", "weight": "350мл", "desc": "Кофе с молоком и пенкой"},
}

# АКЦИИ И ПРЕДЛОЖЕНИЯ
PROMOTIONS = [
    "🔥 Понедельник: Скидка 20% на все торты!",
    "🎁 Вторник: Каждый 3-й кофе в подарок!",
    "👨‍👩‍👧‍👦 Среда: Семейный набор пирожков 6+1 бесплатно!",
    "🎂 Четверг: Предзаказ тортов - скидка 15%!",
    "⭐️ Пятница: Двойные бонусы за каждый заказ!",
    "🍰 Суббота: Бесплатный десерт к заказу от 1000₽!",
    "☕️ Воскресенье: Кофе + круассан = 250₽!",
]

# ГЛАВНОЕ МЕНЮ
def get_main_menu():
    keyboard = [
        [KeyboardButton("🍰 Каталог"), KeyboardButton("🛒 Корзина")],
        [KeyboardButton("📋 Категории"), KeyboardButton("⭐️ Акции")],
        [KeyboardButton("ℹ️ О нас"), KeyboardButton("📞 Контакты")],
        [KeyboardButton("📝 Мои заказы"), KeyboardButton("💎 Бонусы")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== КОМАНДЫ БОТА ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие"""
    user = update.effective_user
    welcome = f"""
✨ *Добро пожаловать в пекарню "Эдем", {user.first_name}!* ✨

🍞 Свежая выпечка каждый день
🎂 Авторские торты на заказ
🥐 Ароматный кофе и десерты

*Выберите действие в меню ниже:*
"""
    await update.message.reply_text(welcome, reply_markup=get_main_menu(), parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - помощь"""
    help_text = """
*📚 Доступные команды:*

*/start* - Главное меню
*/help* - Эта справка  
*/menu* - Показать меню
*/catalog* - Каталог товаров
*/cart* - Корзина
*/promo* - Акции сегодня
*/about* - О пекарне
*/contacts* - Контакты
*/order* - Быстрый заказ

*Кнопки в меню:*
🍰 *Каталог* - все товары
📋 *Категории* - товары по категориям
🛒 *Корзина* - ваш заказ
⭐️ *Акции* - специальные предложения
ℹ️ *О нас* - информация
📞 *Контакты* - как нас найти
📝 *Мои заказы* - история заказов
💎 *Бонусы* - бонусная программа
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /menu - показать меню"""
    await update.message.reply_text("Вот главное меню:", reply_markup=get_main_menu())

async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /catalog - каталог товаров"""
    await show_catalog(update, context)

async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /cart - корзина"""
    await show_cart(update, context)

async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /promo - акции"""
    await show_promotions(update, context)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /about - о пекарне"""
    await about_us(update, context)

async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /contacts - контакты"""
    await contacts_info(update, context)

async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /order - быстрый заказ"""
    text = """
*🚀 Быстрый заказ:*

Чтобы быстро оформить заказ:
1. Посмотрите каталог: /catalog
2. Добавьте товары в корзину
3. Перейдите в корзину: /cart
4. Оформите заказ

Или выберите популярные товары:
"""
    keyboard = [
        [InlineKeyboardButton("🥐 Круассан (120₽)", callback_data="quick_1")],
        [InlineKeyboardButton("☕️ Капучино (180₽)", callback_data="quick_4")],
        [InlineKeyboardButton("🥟 Пирожок (85₽)", callback_data="quick_5")],
        [InlineKeyboardButton("🍪 Печенье (65₽)", callback_data="quick_7")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==================== ОБРАБОТЧИКИ КНОПОК МЕНЮ ====================

async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать каталог товаров"""
    text = "*🍰 Каталог товаров:*\n\n"
    
    for pid, product in PRODUCTS.items():
        text += f"*{pid}.* {product['name']} - {product['price']} ₽\n"
    
    text += "\n*Выберите товар для подробной информации:*"
    
    keyboard = []
    row = []
    for pid in range(1, 7):  # Первые 6 товаров
        product = PRODUCTS[pid]
        row.append(InlineKeyboardButton(f"{pid}", callback_data=f"info_{pid}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("📋 По категориям", callback_data="categories")])
    keyboard.append([InlineKeyboardButton("🔙 В меню", callback_data="back_menu")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать категории товаров"""
    text = "*📋 Категории товаров:*\n\nВыберите категорию:"
    
    categories = {}
    for product in PRODUCTS.values():
        category = product['category']
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(
            f"{category} ({categories[category]} товаров)",
            callback_data=f"category_{category}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 В каталог", callback_data="back_catalog")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Показать товары категории"""
    query = update.callback_query
    text = f"*📋 {category}:*\n\n"
    
    category_products = []
    for pid, product in PRODUCTS.items():
        if product['category'] == category:
            category_products.append((pid, product))
    
    for pid, product in category_products:
        text += f"• {product['name']} - {product['price']} ₽\n"
    
    keyboard = []
    for pid, product in category_products:
        keyboard.append([InlineKeyboardButton(
            f"{product['name']} - {product['price']} ₽",
            callback_data=f"info_{pid}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 К категориям", callback_data="categories")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать корзину"""
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
    
    # Расчет скидки
    discount = 0
    if total > 1000:
        discount = total * 0.1  # 10% скидка
        text += f"\n🎉 *Скидка 10%: -{discount:.0f} ₽*"
    
    final_total = total - discount
    text += f"\n*💰 Итого к оплате: {final_total:.0f} ₽*"
    
    keyboard = []
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        keyboard.append([
            InlineKeyboardButton(f"➖ {product['name'][:10]}", callback_data=f"dec_{pid}"),
            InlineKeyboardButton(f"{quantity}", callback_data="none"),
            InlineKeyboardButton(f"➕", callback_data=f"inc_{pid}")
        ])
    
    if cart:
        keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
        keyboard.append([InlineKeyboardButton("🗑️ Очистить корзину", callback_data="clear_cart")])
    
    keyboard.append([InlineKeyboardButton("🍰 Продолжить покупки", callback_data="back_catalog")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_promotions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать акции"""
    day_of_week = datetime.now().weekday()  # 0 = понедельник
    today_promo = PROMOTIONS[day_of_week]
    
    text = f"*⭐️ Акции и предложения:*\n\n"
    text += f"*Сегодня ({['Пн','Вт','Ср','Чт','Пт','Сб','Вс'][day_of_week]}):*\n{today_promo}\n\n"
    text += "*Все акции недели:*\n"
    
    for i, promo in enumerate(PROMOTIONS):
        text += f"• {promo}\n"
    
    text += "\n*🎁 Бонусная программа:*\n"
    text += "• 1 бонус = 1 рубль\n"
    text += "• Начисляем 5% от суммы заказа\n"
    text += "• Можно оплачивать до 50% заказа бонусами\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """О пекарне"""
    text = """
*🍞 Пекарня "Эдем"*

Основана в 2010 году. Мы создаем вкусные воспоминания!

*Наша философия:*
✅ Только натуральные ингредиенты
✅ Ручная работа мастера-пекаря
✅ Свежесть каждый день
✅ Теплая атмосфера уюта

*Технологии:*
• Дровяная печь для хлеба
• Современное оборудование для кондитерских
• Собственная кофейная станция
• Система контроля качества

*Статистика:*
🏪 1 пекарня в центре города
👨‍🍳 15 профессиональных пекарей
🍞 50+ видов продукции ежедневно
⭐️ 4.9/5 оценка клиентов
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def contacts_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Контакты"""
    text = """
*📞 Наши контакты:*

*Адрес:* ул. Пекарская, 15 (центр города)
*Телефон:* +7 (999) 123-45-67
*Email:* edem@bakery.ru
*Instagram:* @edem_bakery
*Telegram канал:* @edem_bakery_news

*Часы работы:*
Пн-Пт: 7:00 - 22:00
Сб-Вс: 8:00 - 23:00

*Доставка:*
🚗 Бесплатно при заказе от 1000 ₽
⏱️ 60-90 минут в пределах города
📍 Зона доставки: 5 км от пекарни

*Самовывоз:*
🏪 ул. Пекарская, 15
⏰ Бесплатно, 15 минут на подготовку
🎁 Упаковка в подарочную коробку +100₽
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Мои заказы"""
    text = """
*📝 История заказов:*

*Последний заказ:* #4231 (15.12.2024)
• 🥐 Круассан × 2 = 240₽
• ☕️ Капучино × 1 = 180₽
• 🍪 Печенье × 3 = 195₽
*Итого:* 615₽
*Статус:* ✅ Выполнен

*Всего заказов:* 7
*Общая сумма:* 4,850₽
*Накоплено бонусов:* 242💎

*Самый популярный товар:* Круассан (5 раз)
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def bonuses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Бонусная программа"""
    text = """
*💎 Бонусная программа "Эдем":*

*Ваш баланс:* 242 бонуса (242₽)

*Как работают бонусы:*
🎁 1 бонус = 1 рубль
💰 Начисляем 5% от суммы каждого заказа
💳 Можно оплачивать до 50% заказа бонусами
📈 Накопленные бонусы не сгорают

*Уровни программы:*
🥉 *Новичок* (0-1000₽) - 5% бонусов
🥈 *Постоянный* (1000-5000₽) - 7% бонусов + приветственный подарок
🥇 *VIP* (5000+₽) - 10% бонусов + персональная скидка 5% + бесплатная доставка

*Ваш уровень:* 🥈 Постоянный клиент
*До VIP уровня осталось:* 150₽

*Специальные предложения:*
🎂 День рождения: двойные бонусы
👫 Приведи друга: +200 бонусов каждому
📅 Праздники: дополнительные бонусы
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== ОБРАБОТЧИКИ ИНЛАЙН-КНОПОК ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("info_"):
        pid = int(data.split("_")[1])
        product = PRODUCTS[pid]
        
        text = f"""
*{product['name']}*

*Описание:* {product['desc']}
*Цена:* {product['price']} ₽
*Вес:* {product['weight']}
*Категория:* {product['category']}

Добавить в корзину?
"""
        keyboard = [
            [InlineKeyboardButton("➕ Добавить в корзину", callback_data=f"add_{pid}")],
            [InlineKeyboardButton("🔙 В каталог", callback_data="back_catalog")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif data.startswith("add_"):
        pid = data.split("_")[1]
        
        if 'cart' not in context.user_data:
            context.user_data['cart'] = {}
        
        cart = context.user_data['cart']
        cart[pid] = cart.get(pid, 0) + 1
        
        product = PRODUCTS[int(pid)]
        await query.answer(f"✅ {product['name']} добавлен в корзину!")
    
    elif data.startswith("inc_"):
        pid = data.split("_")[1]
        cart = context.user_data.get('cart', {})
        cart[pid] = cart.get(pid, 0) + 1
        await show_cart_from_query(query, context)
    
    elif data.startswith("dec_"):
        pid = data.split("_")[1]
        cart = context.user_data.get('cart', {})
        if pid in cart:
            if cart[pid] > 1:
                cart[pid] -= 1
            else:
                del cart[pid]
        await show_cart_from_query(query, context)
    
    elif data == "categories":
        await show_categories_from_query(query, context)
    
    elif data.startswith("category_"):
        category = data.split("_")[1]
        await show_category_products_from_query(query, context, category)
    
    elif data == "checkout":
        await checkout_order(query, context)
    
    elif data == "clear_cart":
        context.user_data['cart'] = {}
        await query.answer("Корзина очищена!", show_alert=True)
        await query.edit_message_text("🛒 *Корзина очищена!*", parse_mode='Markdown')
    
    elif data == "back_menu":
        await start_from_query(query, context)
    
    elif data == "back_catalog":
        await show_catalog_from_query(query, context)

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
    
    discount = total * 0.1 if total > 1000 else 0
    final_total = total - discount
    
    if discount > 0:
        text += f"\n🎉 *Скидка 10%: -{discount:.0f} ₽*"
    
    text += f"\n*💰 Итого к оплате: {final_total:.0f} ₽*"
    
    keyboard = []
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        keyboard.append([
            InlineKeyboardButton(f"➖ {product['name'][:10]}", callback_data=f"dec_{pid}"),
            InlineKeyboardButton(f"{quantity}", callback_data="none"),
            InlineKeyboardButton(f"➕", callback_data=f"inc_{pid}")
        ])
    
    keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🔙 В меню", callback_data="back_menu")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def checkout_order(query, context):
    cart = context.user_data.get('cart', {})
    
    if not cart:
        await query.answer("Корзина пуста!", show_alert=True)
        return
    
    total = 0
    order_details = ""
    for pid, quantity in cart.items():
        product = PRODUCTS[int(pid)]
        item_total = product['price'] * quantity
        total += item_total
        order_details += f"• {product['name']} - {quantity} шт. = {item_total} ₽\n"
    
    discount = total * 0.1 if total > 1000 else 0
    final_total = total - discount
    
    order_number = random.randint(1000, 9999)
    
    text = f"""
✅ *Заказ оформлен!*

*Номер заказа:* #{order_number}
*Дата:* {datetime.now().strftime("%d.%m.%Y %H:%M")}

*Ваш заказ:*
{order_details}
"""
    
    if discount > 0:
        text += f"\n🎉 *Скидка 10%: -{discount:.0f} ₽*"
    
    text += f"""
*💰 Итого к оплате: {final_total:.0f} ₽*

*Выберите способ получения:*
"""
    
    keyboard = [
        [InlineKeyboardButton("🚗 Доставка (+200₽)", callback_data="delivery")],
        [InlineKeyboardButton("🏪 Самовывоз (бесплатно)", callback_data="pickup")],
        [InlineKeyboardButton("📞 Позвонить для уточнения", callback_data="call_me")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start_from_query(query, context):
    welcome = "✨ *Добро пожаловать!* ✨"
    await query.edit_message_text(welcome, reply_markup=get_main_menu(), parse_mode='Markdown')

async def show_catalog_from_query(query, context):
    text = "*🍰 Каталог товаров:*\n\n"
    
    for pid, product in PRODUCTS.items():
        text += f"*{pid}.* {product['name']} - {product['price']} ₽\n"
    
    keyboard = []
    for pid in range(1, 7):
        keyboard.append([InlineKeyboardButton(f"Товар {pid}", callback_data=f"info_{pid}")])
    
    keyboard.append([InlineKeyboardButton("🔙 В меню", callback_data="back_menu")])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_categories_from_query(query, context):
    text = "*📋 Категории товаров:*\n\n"
    
    categories = {}
    for product in PRODUCTS.values():
        category = product['category']
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(
            f"{category} ({categories[category]} товаров)",
            callback_data=f"category_{category}"
        )])
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_category_products_from_query(query, context, category):
    text = f"*📋 {category}:*\n\n"
    
    for pid, product in PRODUCTS.items():
        if product['category'] == category:
            text += f"• {product['name']} - {product['price']} ₽\n"
    
    keyboard = [[InlineKeyboardButton("🔙 К категориям", callback_data="categories")]]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("catalog", catalog_command))
    application.add_handler(CommandHandler("cart", cart_command))
    application.add_handler(CommandHandler("promo", promo_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("contacts", contacts_command))
    application.add_handler(CommandHandler("order", order_command))
    
    # Регистрация обработчиков кнопок меню
    application.add_handler(MessageHandler(filters.Regex("^🍰 Каталог$"), show_catalog))
    application.add_handler(MessageHandler(filters.Regex("^📋 Категории$"), show_categories))
    application.add_handler(MessageHandler(filters.Regex("^🛒 Корзина$"), show_cart))
    application.add_handler(MessageHandler(filters.Regex("^⭐️ Акции$"), show_promotions))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ О нас$"), about_us))
    application.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts_info))
    application.add_handler(MessageHandler(filters.Regex("^📝 Мои заказы$"), my_orders))
    application.add_handler(MessageHandler(filters.Regex("^💎 Бонусы$"), bonuses))
    
    # Регистрация инлайн-кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("=" * 70)
    print("🚀 БОТ ПЕКАРНИ 'ЭДЕМ' ЗАПУЩЕН")
    print("=" * 70)
    print("📱 Доступные команды в Telegram:")
    print("• /start - Главное меню")
    print("• /help - Помощь по командам")
    print("• /menu - Показать меню")
    print("• /catalog - Каталог товаров")
    print("• /cart - Корзина")
    print("• /promo - Акции")
    print("• /about - О пекарне")
    print("• /contacts - Контакты")
    print("• /order - Быстрый заказ")
    print("=" * 70)
    print("✅ Бот готов к работе! Откройте Telegram и напишите /start")
    print("=" * 70)
    
    application.run_polling()

if __name__ == "__main__":
    main()