import telebot
from telebot import types
import random
import os

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

wallets = {}
services = {}
history_data = {}

# قیمت = 199000 × تعداد گیگ
configs = {
    "1 گیگ": {"price": 199000 * 1, "details": "سرویس 1 گیگ پرسرعت"},
    "2 گیگ": {"price": 199000 * 2, "details": "سرویس 2 گیگ پرسرعت"},
    "4 گیگ": {"price": 199000 * 4, "details": "سرویس 4 گیگ پرسرعت"},
    "5 گیگ": {"price": 199000 * 5, "details": "سرویس 5 گیگ پرسرعت"},
    "6 گیگ": {"price": 199000 * 6, "details": "سرویس 6 گیگ پرسرعت"},
    "10 گیگ (تخفیف ویژه)": {"price": 199000 * 8, "details": "سرویس 10 گیگ با تخفیف"},
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
    bot.send_message(message.chat.id,
        f"خوش اومدی {first_name} 🌹\n"
        f"برای خرید سرویس فقط از طریق ربات اقدام کن.\n"
        f"پشتیبانی: {SUPPORT_USERNAME}",
        reply_markup=markup
    )

# ------------------ فروشگاه ------------------
@bot.message_handler(func=lambda m: m.text == "🛒 فروشگاه")
def shop(message):
    text = "📦 لیست سرویس‌ها:\n\n"
    for name, info in configs.items():
        text += f"🔹 {name}: {info['price']} تومان\n"
    bot.send_message(message.chat.id, text)

# ------------------ کیف پول ------------------
@bot.message_handler(func=lambda m: m.text == "💰 کیف پول")
def wallet(message):
    balance = wallets.get(message.chat.id, {}).get("balance", 0)
    bot.send_message(message.chat.id, f"💰 موجودی شما: {balance} تومان\nبرای شارژ دستور /charge را بزن.")

@bot.message_handler(commands=['charge'])
def charge_wallet(message):
    bot.send_message(message.chat.id, "لطفاً مبلغ شارژ را وارد کنید (عدد خالی).")

@bot.message_handler(func=lambda m: m.text.isdigit())
def get_amount(message):
    amount = int(message.text)
    unique = random.randint(11, 99)
    final_amount = amount + unique

    wallets[message.chat.id] = {
        "pending": final_amount,
        "balance": wallets.get(message.chat.id, {}).get("balance", 0)
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 کپی شماره کارت", switch_inline_query=CARD_NUMBER))

    bot.send_message(
        message.chat.id,
        f"✅ مبلغ {amount} ثبت شد.\n"
        f"لطفاً دقیقاً {final_amount} تومان واریز کنید.\n\n"
        f"💳 شماره کارت: {CARD_NUMBER}\n👤 به نام: {CARD_NAME}\n\n"
        f"📩 بعد از واریز، رسید را ارسال کنید.",
        reply_markup=markup
    )

# ------------------ دریافت رسید ------------------
@bot.message_handler(content_types=['photo', 'document'])
def receive_receipt(message):
    if message.chat.id in wallets and "pending" in wallets[message.chat.id]:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ تایید", callback_data=f"confirm_{message.chat.id}"),
            types.InlineKeyboardButton("❌ رد", callback_data=f"reject_{message.chat.id}")
        )

        bot.send_message(ADMIN_ID, f"رسید کاربر {message.chat.id} دریافت شد.", reply_markup=markup)
        bot.send_message(message.chat.id, "📩 رسید ارسال شد. منتظر تایید مدیر باشید.")

# ------------------ تایید / رد ------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data.startswith("reject_"))
def admin_action(call):
    user_id = int(call.data.split("_")[1])

    if call.data.startswith("confirm_"):
        amount = wallets[user_id]["pending"]
        wallets[user_id]["balance"] += amount
        del wallets[user_id]["pending"]

        bot.send_message(user_id, f"✅ شارژ {amount} تومان تایید شد.\nموجودی جدید: {wallets[user_id]['balance']} تومان")
        bot.send_message(ADMIN_ID, f"شارژ کاربر {user_id} تایید شد.")

    else:
        del wallets[user_id]["pending"]
        bot.send_message(user_id, "❌ رسید شما رد شد.")
        bot.send_message(ADMIN_ID, f"رسید کاربر {user_id} رد شد.")

# ------------------ سرویس‌های من ------------------
@bot.message_handler(func=lambda m: m.text == "📦 سرویس‌های من")
def my_services(message):
    user_services = services.get(message.chat.id, [])
    if user_services:
        bot.send_message(message.chat.id, "📦 سرویس‌های فعال شما:\n" + "\n".join(user_services))
    else:
        bot.send_message(message.chat.id, "❌ هیچ سرویس فعالی ندارید.")

# ------------------ استعلام موجودی ------------------
@bot.message_handler(func=lambda m: m.text == "📊 استعلام موجودی")
def check_balance(message):
    balance = wallets.get(message.chat.id, {}).get("balance", 0)
    bot.send_message(message.chat.id, f"📊 موجودی فعلی شما: {balance} تومان")

# ------------------ تیکت پشتیبانی ------------------
@bot.message_handler(func=lambda m: m.text == "🎫 تیکت پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, f"برای پشتیبانی پیام بده:\n{SUPPORT_USERNAME}")

# ------------------ حساب من ------------------
@bot.message_handler(func=lambda m: m.text == "👤 حساب من")
def my_account(message):
    first_name = message.from_user.first_name
    username = message.from_user.username or "ثبت نشده"
    bot.send_message(message.chat.id, f"👤 نام: {first_name}\n🔗 یوزرنیم: @{username}")

# ------------------ تاریخچه ------------------
@bot.message_handler(func=lambda m: m.text == "📜 تاریخچه")
def history(message):
    user_history = history_data.get(message.chat.id, [])
    if user_history:
        bot.send_message(message.chat.id, "📜 تاریخچه خرید:\n" + "\n".join(user_history))
    else:
        bot.send_message(message.chat.id, "❌ هیچ خریدی ثبت نشده است.")

# ------------------ خرید همکاری ------------------
@bot.message_handler(func=lambda m: m.text == "🤝 خرید همکاری")
def coop(message):
    bot.send_message(message.chat.id, f"برای همکاری پیام بده:\n{SUPPORT_USERNAME}")

bot.polling(none_stop=True)
