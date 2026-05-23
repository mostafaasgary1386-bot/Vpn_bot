import telebot
from telebot import types
import random
import os

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

wallets = {}
services = {}

# لیست آیدی‌ها برای همکاری
cooperators = [123456789]        # آیدی همکاری معمولی (تو اضافه می‌کنی)
bulk_cooperators = [987654321]   # آیدی همکاری تعداد بالا (تو اضافه می‌کنی)

configs = {
    "1 گیگ": {
        "price": 199000,
        "details": "کانفیگ 1 گیگ پرسرعت",
        "stock": 5,
        "pairs": [
            {
                "service": "vless://28f5a2f8-1920-4de8-95bb-f6145a2e4b25@meli2.masterdadeh.ir:80?type=ws&security=none&path=%2F&headerType=none#JXZ2wG-Bot",
                "sub": "https://185.226.94.193:2096/sub/ff7efbd84fc479de"
            },
            {
                "service": "vless://4d056db9-b98e-4bb4-805f-c1f7e82dd185@meli2.masterdadeh.ir:80?type=ws&security=none&path=%2F&headerType=none#Q0qCyF-Bot",
                "sub": "https://185.226.94.193:2096/sub/84da5303d688ca77"
            },
            {
                "service": "vless://c5d8a286-3cbd-4a00-96a0-63750b03bf64@meli2.masterdadeh.ir:80?type=ws&security=none&path=%2F&headerType=none#QJlAEe-Bot",
                "sub": "https://185.226.94.193:2096/sub/6a48839e3c03226d"
            },
            {
                "service": "vless://4c54c7e5-148d-49ae-9f65-b66e229b8e17@meli2.masterdadeh.ir:80?type=ws&security=none&path=%2F&headerType=none#71VmBe-Bot",
                "sub": "https://185.226.94.193:2096/sub/aa691bd89e657a69"
            },
            {
                "service": "vless://611cc6e6-4c1d-4398-84c3-5ef6680ba4ac@meli2.masterdadeh.ir:80?type=ws&security=none&path=%2F&headerType=none#HorCiJ-Bot",
                "sub": "https://185.226.94.193:2096/sub/104dcd949c4ab31b"
            }
        ]
    },
    "2 گیگ": {"price": 398000, "details": "کانفیگ 2 گیگ پرسرعت", "stock": 0, "pairs": []},
    "4 گیگ": {"price": 796000, "details": "کانفیگ 4 گیگ پرسرعت", "stock": 0, "pairs": []},
    "5 گیگ": {"price": 995000, "details": "کانفیگ 5 گیگ پرسرعت", "stock": 0, "pairs": []},
}

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
    markup.row("📜 تاریخچه")
    bot.send_message(message.chat.id, f"سلام {first_name} 👋\nبه ربات فروش خوش آمدی.", reply_markup=markup)

# --- فروشگاه ---
@bot.message_handler(func=lambda m: m.text == "🛒 فروشگاه")
def shop(message):
    markup = types.InlineKeyboardMarkup()
    for name, info in configs.items():
        btn = types.InlineKeyboardButton(
            text=f"{name} - {info['price']} تومان (موجودی: {info['stock']})",
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
        if info["stock"] > 0 and info["pairs"]:
            gig_count = int(config_name.split()[0])
            if user_id in bulk_cooperators:
                price = 120000 * gig_count
            elif user_id in cooperators:
                price = 150000 * gig_count
            else:
                price = info["price"]

            balance = wallets.get(user_id, {}).get("balance", 0)
            if balance >= price:
                wallets[user_id]["balance"] -= price
                info["stock"] -= 1

                pair = info["pairs"].pop(0)
                service_link = pair["service"]
                sub_link = pair["sub"]

                services.setdefault(user_id, []).append(
                    f"{config_name}\n🔗 سرویس: {service_link}\n🔗 ساب: {sub_link}"
                )

                bot.send_message(user_id,
                    f"✅ خرید {config_name} موفق بود.\n"
                    f"💰 قیمت: {price} تومان\n"
                    f"🔗 سرویس: {service_link}\n"
                    f"🔗 ساب: {sub_link}"
                )
            else:
                bot.send_message(user_id, "❌ موجودی کیف پول کافی نیست. لطفاً شارژ کنید.")
        else:
            bot.send_message(user_id, f"❌ موجودی {config_name} تمام شده یا لینک‌ها موجود نیست.")

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
    
    bot.send_message(message.chat.id,
        f"✅ مبلغ {amount} تومان ثبت شد.\n"
        f"برای تایید رسید لطفاً دقیقاً {final_amount} تومان واریز کنید.\n\n"
        f"💳 شماره کارت:\n`{CARD_NUMBER}`\n👤 به نام: {CARD_NAME}\n\n"
        f"📩 بعد از واریز، رسید پرداخت رو ارسال کنید.",
        parse_mode="Markdown"
    )

# --- دریافت رسید ---
@bot.message_handler(content_types=['photo', 'document', 'text'])
def receive_receipt(message):
    if message.chat.id in wallets and "pending" in wallets[message.chat.id]:
        bot.send_message(message.chat.id, "📩 رسید شما ارسال شد. منتظر تایید مدیر باشید.")

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
    bot.send_message(message.chat.id, f"📩 برای پشتیبانی لطفاً پیام خود را ارسال کنید.\nادمین: {SUPPORT_USERNAME}")

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

# --- اجرای ربات ---
bot.polling(none_stop=True)
