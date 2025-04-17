import telebot
from telebot import types
import requests

BOT_TOKEN = "7286664216:AAGzdMYKPyBtNJ6WJ2m0gKlaWRiy6RPNif8"
MAIN_BOT_TOKEN = "8039468185:AAFqmCnNT95iPFFzPd7b_oew_8ur1SgYGik"
ADMIN_ID = 630292149
GUIDE_LINK = 'https://t.me/+RwBF8E4D0RJlNmYy'

bot = telebot.TeleBot(BOT_TOKEN)
user_photos = {}  # message_id → user_id

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'без username'

    forwarded = bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    user_photos[forwarded.message_id] = user_id

    bot.reply_to(message, "Скриншот получен! Ожидай подтверждения.")

    # Кнопки "Одобрить" и "Отклонить"
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{forwarded.message_id}")
    decline_btn = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{forwarded.message_id}")
    markup.row(approve_btn, decline_btn)

    bot.send_message(ADMIN_ID, f"Чек от @{username}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("decline_"))
def handle_decision(call):
    action, msg_id = call.data.split("_")
    msg_id = int(msg_id)
    user_id = user_photos.get(msg_id)

    if not user_id:
        bot.answer_callback_query(call.id, "Пользователь не найден.")
        return

    if action == "approve":
        response = requests.post(
            f"https://api.telegram.org/bot{MAIN_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": user_id,
                "text": f"✅ Оплата подтверждена!\nВот ссылка на гайд: {GUIDE_LINK}"
            }
        )
        if response.status_code == 200:
            bot.answer_callback_query(call.id, "Доступ выдан.")
        else:
            bot.answer_callback_query(call.id, "Ошибка при отправке.")
    elif action == "decline":
        response = requests.post(
            f"https://api.telegram.org/bot{MAIN_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": user_id,
                "text": "❌ Чек не принят. Пожалуйста, пришли корректный скриншот оплаты."
            }
        )
        if response.status_code == 200:
            bot.answer_callback_query(call.id, "Отказ отправлен.")
        else:
            bot.answer_callback_query(call.id, "Ошибка при отказе.")

bot.remove_webhook()
bot.polling()