from flask import Flask, request
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '7549837458:AAFE1zz6dh24JYr5ufJx3JuBYeJHMYg8eaw'  # 🔁 Замени на свой токен
ADMIN_ID = 354773080  # 🔁 Замени на свой Telegram ID
WEBHOOK_HOST = 'https://zelinski-order-bot-q6hw.onrender.com'  # 🔁 Вставь сюда URL своего сервиса Render
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Flask(name)

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("🛍 Каталог"), KeyboardButton("📦 Оформить заказ"))

products = {
    "Крем Лаванда-Пачули": "250 мл — 4 200 ₽",
    "Мыло Cedarwood": "150 г — 2 000 ₽",
    "Масло для тела Rose": "200 мл — 4 800 ₽"
}

user_order = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот по косметике Zelinski & Rozen. Что вас интересует?", reply_markup=menu)

@dp.message_handler(lambda message: message.text == "🛍 Каталог")
async def show_catalog(message: types.Message):
    text = "🌿 *Каталог продуктов:*\n\n"
    for name, price in products.items():
        text += f"— *{name}* — {price}\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "📦 Оформить заказ")
async def order_start(message: types.Message):
    user_order[message.chat.id] = {}
    await message.answer("Введите ваше *имя*:", parse_mode="Markdown")

@dp.message_handler(lambda message: message.chat.id in user_order and 'name' not in user_order[message.chat.id])
async def get_name(message: types.Message):
    user_order[message.chat.id]['name'] = message.text
    await message.answer("Введите ваш *адрес доставки*:", parse_mode="Markdown")

@dp.message_handler(lambda message: message.chat.id in user_order and 'address' not in user_order[message.chat.id])
async def get_address(message: types.Message):
    user_order[message.chat.id]['address'] = message.text
    await message.answer("Введите ваш *номер телефона* для связи:", parse_mode="Markdown")

@dp.message_handler(lambda message: message.chat.id in user_order and 'phone' not in user_order[message.chat.id])
async def get_phone(message: types.Message):
    user_order[message.chat.id]['phone'] = message.text
    data = user_order[message.chat.id]
    msg = (
        f"🎉 *Новый заказ!*\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🏠 Адрес: {data['address']}\n"
        f"📞 Телефон: {data['phone']}"
    )
    await bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
    await message.answer("Спасибо за заказ! Мы с вами свяжемся в ближайшее время. 🌸")
    del user_order[message.chat.id]

@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook():
    update = types.Update(**request.json)
    await dp.process_update(update)
    return 'ok'

async def on_startup():
    # Устанавливаем webhook при старте приложения
    await bot.set_webhook(WEBHOOK_URL)

if name == 'main':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=8080)
