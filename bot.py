import telebot
from telebot import types
import random
import os

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

wallets = {}
services = {}

configs = {
    "1 گیگ": {"price": 199000 * 1, "details": "کانفیگ 1 گیگ پرسرعت"},
    "2 گیگ": {"price": 199000 * 2, "details": "کانفیگ 2 گیگ پرسرعت"},
    "4 گیگ": {"price": 199000 * 4, "details": "کانفیگ 4 گیگ پرسرعت"},
    "5 گیگ": {"price": 199000 * 5, "details": "کانفیگ 5 گیگ پرسرعت"},
    "6 گیگ": {"price": 199000 * 6, "details": "کانفیگ 6 گیگ پرسرعت"},
}

ADMIN_ID = 5048925895
CARD_NUMBER = "5022291581967849"
CARD_NAME = "مصطفی عسگری"
SUPPORT_USERNAME = "@kayavpnadmin"

# ------------------ منوی اصلی ------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    first_name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 فروشگاه", "💰 کیف پول")
    markup.row("📦 سرویس‌های من", "📊 استعلام موجودی")
    markup.row("🎫 تیکت پشتیبانی", "👤 حساب من")
    markup.row("📜 تاریخچه", "🤝 خرید همکاری")
    bot.send_message(message.chat.id, f"سلام {first_name} 👋", reply_markup=markup)

# ------------------ فروشگاه ------------------
@bot.message_handler(func=lambda m: m.text == "🛒 فروشگاه")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for name, info in configs.items():
        btn = types.InlineKeyboardButton(
            text=f"{name} - {info['price']} تومان",
            callback_data=f"buy_{name}"
        )
        markup.add(btn)
    bot.send_message(message.chat.id, "📦 لیست کانفیگ‌ها:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_buy(call):
    config_name = call.data.replace("buy_", "")
    info = configs.get(config_name)
    user_id = call.message.chat.id

    if info:
        balance = wallets.get(user_id, {}).get("balance", 0)
        if balance >= info["price"]:
            wallets[user_id]["balance"] -= info["price"]
            services.setdefault(user_id, []).append(config_name)
            bot.send_message(user_id, f"✅ خرید {config_name} انجام شد.\n{info['details']}")
        else:
            bot.send_message(user_id, "❌ موجودی کافی نیست.")

# ------------------ کیف پول ------------------
@bot.message_handler(func=lambda m: m.text == "💰 کیف پول")
def wallet(message):
    balance = wallets.get(message.chat.id, {}).get("balance", 0)
    bot.send_message(message.chat.id, f"💰 موجودی شما: {balance} تومان\n/charge را بزن.")

@bot.message_handler(commands=['charge'])
def charge_wallet(message):
    bot.send_message(message.chat.id, "مبلغ شارژ را وارد کنید:")

@bot.message_handler(func=lambda m: m.text.isdigit())
def get_amount(message):
    amount = int(message.text)
    unique = random.randint(11, 99)
    final_amount = amount + unique

    wallets[message.chat.id] = {
        "pending": final_amount,
        "balance": wallets.get(message.chat.id, {}).get("balance", 0)
    }

    bot.send_message(
        message.chat.id,
        f"مبلغ {amount} ثبت شد.\n"
        f"لطفاً دقیقاً {final_amount} تومان واریز کنید.\n\n"
        f"💳 کارت: {CARD_NUMBER}\n👤 {CARD_NAME}",
        parse_mode="Markdown"
    )

# ------------------ دریافت رسید ------------------
@bot.message_handler(content_types=['photo', 'document', 'text'])
def receive_receipt(message):
    if message.chat.id in wallets and "pending" in wallets[message.chat.id]:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("تایید", callback_data=f"confirm_{message.chat.id}"),
            types.InlineKeyboardButton("رد", callback_data=f"reject_{message.chat.id}")
        )

        bot.send_message(ADMIN_ID, f"رسید کاربر {message.chat.id}:", reply_markup=markup)
        bot.send_message(message.chat.id, "رسید ارسال شد.")

# ------------------ تایید / رد ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data.startswith("reject_"))
def admin_action(call):
    user_id = int(call.data.split("_")[1])

    if call.data.startswith("confirm_"):
        amount = wallets[user_id]["pending"]
        wallets[user_id]["balance"] += amount
        del wallets[user_id]["pending"]
        bot.send_message(user_id, f"شارژ {amount} تایید شد.")
    else:
        del wallets[user_id]["pending"]
        bot.send_message(user_id, "رسید رد شد.")

# ------------------ سرویس‌های من ------------------
@bot.message_handler(func=lambda m: m.text == "📦 سرویس‌های من")
def my_services(message):
    user_services = services.get(message.chat.id, [])
    if user_services:
        bot.send_message(message.chat.id, "\n".join(user_services))
    else:
        bot.send_message(message.chat.id, "سرویسی ندارید.")

# ------------------ تیکت پشتیبانی ------------------
@bot.message_handler(func=lambda m: m.text == "🎫 تیکت پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, f"برای پشتیبانی پیام بده:\n{kayavpnadmin}")

# ------------------ حساب من ------------------
@bot.message_handler(func=lambda m: m.text == "👤 حساب من")
def my_account(message):
    first_name = message.from_user.first_name
    username = message.from_user.username or "ندارد"
    bot.send_message(message.chat.id, f"نام: {first_name}\nیوزرنیم: @{username}")

# ------------------ تاریخچه ------------------
@bot.message_handler(func=lambda m: m.text == "📜 تاریخچه")
def history(message):
    user_services = services.get(message.chat.id, [])
    if user_services:
        bot.send_message(message.chat.id, "\n".join(user_services))
    else:
        bot.send_message(message.chat.id, "تاریخی وجود ندارد.")

# ------------------ خرید همکاری ------------------
@bot.message_handler(func=lambda m: m.text == "🤝 خرید همکاری")
def coop(message):
    bot.send_message(message.chat.id, f"برای همکاری پیام بده:\n{kayavpnadmin}")

bot.polling(none_stop=True)
