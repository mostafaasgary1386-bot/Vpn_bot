import telebot
from telebot import types
import random
import os

# توکن ربات از Environment Variable در Railway
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

wallets = {}
services = {}

# لیست کانفیگ‌ها (قیمت = 199000 * تعداد گیگ)
configs = {
    "1 گیگ": {"price": 199000 * 1, "details": "کانفیگ 1 گیگ پرسرعت"},
    "2 گیگ": {"price": 199000 * 2, "details": "کانفیگ 2 گیگ پرسرعت"},
    "4 گیگ": {"price": 199000 * 4, "details": "کانفیگ 4 گیگ پرسرعت"},
    "5 گیگ": {"price": 199000 * 5, "details": "کانفیگ 5 گیگ پرسرعت"},
    "6 گیگ": {"price": 199000 * 6, "details": "کانفیگ 6 گیگ پرسرعت"},  # اضافه شد
}

ADMIN_ID = 5048925895
CARD_NUMBER = "5022291581967849"
CARD_NAME = "مصطفی عسگری"
SUPPORT_USERNAME = "@kayavpnadmin"

# --- منوی اصلی ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    first_name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛒 فروشگاه", "💰 کیف پول")
    markup.row("📦 سرویس‌های من", "📊 استعلام موجودی")
    markup.row("🎫 تیکت پشتیبانی", "👤 حساب من")
    markup.row("📜 تاریخچه", "🤝 خرید همکاری")
    bot.send_message(
        message.chat.id,
        f"سلام {first_name} 👋\nبه ربات فروش خوش آمدی.",
        reply_markup=markup
    )

# --- فروشگاه ---
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
            bot.send_message(user_id, f"✅ خرید {config_name} موفق بود.\nکانفیگ ارسال شد: {info['details']}")
        else:
            bot.send_message(user_id, "❌ موجودی کیف پول کافی نیست. لطفاً شارژ کنید.")

# --- کیف پول ---
@bot.message_handler(func=lambda m: m.text == "💰 کیف پول")
def wallet(message):
    balance = wallets.get(message.chat.id, {}).get("balance", 0)
    bot.send_message(message.chat.id, f"💰 موجودی کیف پول شما: {balance} تومان\nبرای شارژ دستور /charge رو بزن.")

@bot.message_handler(commands=['charge'])
def charge_wallet(message):
    bot.send_message(message.chat.id, "لطفاً مبلغ مورد نظر برای شارژ رو وارد کن (به تومان).")

@bot.message_handler(func=lambda m: m.text.isdigit())
def get_amount(message):
    amount = int(message.text)
    unique_code = random.randint(11, 99)
    final_amount = amount + unique_code
    
    wallets[message.chat.id] = {
        "pending": final_amount,
        "balance": wallets.get(message.chat.id, {}).get("balance", 0)
    }
    
    bot.send_message(
        message.chat.id,
        f"✅ مبلغ {amount} تومان ثبت شد.\n"
        f"برای تایید رسید لطفاً دقیقاً {final_amount} تومان واریز کنید.\n\n"
        f"💳 شماره کارت:\n{CARD_NUMBER}\n👤 به نام: {CARD_NAME}\n\n"
        f"📩 بعد از واریز، رسید پرداخت رو ارسال کنید.",
        parse_mode="Markdown"
    )

# --- دریافت رسید و ارسال به ادمین ---
@bot.message_handler(content_types=['photo', 'document', 'text'])
def receive_receipt(message):
    if message.chat.id in wallets and "pending" in wallets[message.chat.id]:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("✅ تایید", callback_data=f"confirm_{message.chat.id}")
        btn_no = types.InlineKeyboardButton("❌ رد", callback_data=f"reject_{message.chat.id}")
        markup.add(btn_yes, btn_no)

        bot.send_message(ADMIN_ID, f"📩 رسید کاربر {message.chat.id} دریافت شد. آیا تایید می‌کنید؟", reply_markup=markup)
        bot.send_message(message.chat.id, "📩 رسید شما ارسال شد. منتظر تایید مدیر باشید.")

# --- مدیریت تایید/رد ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data.startswith("reject_"))
def handle_admin_action(call):
    user_id = int(call.data.split("_")[1])

    if call.data.startswith("confirm_"):
        amount = wallets[user_id]["pending"]
        wallets[user_id]["balance"] += amount
        del wallets[user_id]["pending"]
        bot.send_message(user_id, f"✅ شارژ شما به مبلغ {amount} تومان تایید شد.\nموجودی کیف پول: {wallets[user_id]['balance']} تومان")
        bot.send_message(ADMIN_ID, f"کاربر {user_id} با موفقیت شارژ شد.")
    else:
        del wallets[user_id]["pending"]
        bot.send_message(user_id, "❌ رسید شما توسط مدیر رد شد.")
        bot.send_message(ADMIN_ID, f"رسید کاربر {user_id} رد شد.")

# --- سرویس‌های من ---
@bot.message_handler(func=lambda m: m.text == "📦 سرویس‌های من")
def my_services(message):
    user_services = services.get(message.chat.id, [])
    if user_services:
        bot.send_message(message.chat.id, "📦 سرویس‌های فعال شما:\n" + "\n".join(user_services))
    else:
        bot.send_message(message.chat.id, "❌ شما هیچ سرویس فعالی ندارید.")

# --- تیکت پشتیبانی ---
@bot.message_handler(func=lambda m: m.text == "🎫 تیکت پشتیبانی")
def support(message):
    bot.send_message(message.chat.id, f"📩 پیام خود را ارسال کنید.\nادمین: {SUPPORT_USERNAME}")

# --- حساب من ---
@bot.message_handler(func=lambda m: m.text == "👤 حساب من")
def my_account(message):
    first_name = message.from_user.first_name
    username = message.from_user.username or "یوزرنیم ثبت نشده"
    bot.send_message(message.chat.id, f"👤 نام: {first_name}\n🔗 یوزرنیم: @{username}")

# --- تاریخچه ---
@bot.message_handler(func=lambda m: m.text == "📜 تاریخچه")
def history(message):
    user_services = services.get(message.chat.id, [])
    if user_services:
        bot.send_message(message.chat.id, "📜 تاریخچه خریدهای شما:\n" + "\n".join(user_services))
    else:
        bot.send_message(message.chat.id, "❌ هنوز خریدی ثبت نشده است.")

# --- خرید همکاری ---
@bot.message_handler(func=lambda m: m.text == "🤝 خرید همکاری")
def coop_buy(message):
    bot.send_message(
        message.chat.id,
        f"🤝 برای خرید همکاری و دریافت شرایط، به ادمین پیام بده:\n{SUPPORT_USERNAME}"
    )

bot.polling(none_stop=True)
