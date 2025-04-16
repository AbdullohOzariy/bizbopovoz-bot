import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Save credentials before importing sheets
encoded = os.environ.get("SHEETS_CREDENTIALS_JSON")
if not encoded:
    raise RuntimeError("❌ SHEETS_CREDENTIALS_JSON topilmadi!")
with open("credentials.json", "wb") as f:
    f.write(base64.b64decode(encoded))

from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, filters, ConversationHandler
)

from sheets import log_start, log_exit, has_voted, add_vote, generate_stats_chart

# Maktablar ro‘yxati
schools = [
    "18-maktab (shahar)", "10-maktab (shahar)", "7-maktab (shahar)",
    "20-maktab (shahar)", "9-maktab (shahar)", "4-maktab (shahar)",
    "3-maktab (shahar)", "5-maktab (Yo‘lchilar ovuli)", "12-maktab (Shalxar ovuli)"
]

# Conversation bosqichlari
NAME, PHONE, CHECK_SUBSCRIPTION, VOTE = range(4)

# Kanal ID (username yoki -100... formatida)
CHANNEL_ID = "@bizbop_supermarket"  # yoki -100XXXXXXXXXX

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_start(user.id, user.first_name, user.username)

    if has_voted(user.id):
        await update.message.reply_text("Siz allaqachon ovoz bergansiz.")
        return ConversationHandler.END

    await update.message.reply_text(
        "👋 Assalomu alaykum! Bizbop Ovoz botiga xush kelibsiz!\n\nIsmingizni kiriting:"
    )
    return NAME

# Ism olish
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    btn = KeyboardButton("📞 Kontakt yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Telefon raqamingizni yuboring:", reply_markup=markup)
    return PHONE

# Telefon olish
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number

    if has_voted(user_id):
        await update.message.reply_text("❗️Siz allaqachon ovoz bergansiz.")
        return ConversationHandler.END

    context.user_data["phone"] = phone

    inline_btn = InlineKeyboardButton("📢 Kanalga a'zo bo‘lish", url="https://t.me/bizbop_supermarket")
    await update.message.reply_text(
        "📢 Endi kanalga a'zo bo‘ling va pastdagi tugmani bosing:",
        reply_markup=InlineKeyboardMarkup([[inline_btn]])
    )

    markup = ReplyKeyboardMarkup([[KeyboardButton("✅ Obuna bo‘ldim")]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("✅ Obuna bo‘lib bo‘lsangiz, pastdagi tugmani bosing:", reply_markup=markup)
    return CHECK_SUBSCRIPTION

# A'zolikni tekshirish
async def check_subscription_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ("left", "kicked"):
            raise Exception("Not subscribed")

        markup = ReplyKeyboardMarkup(
            [schools[i:i + 3] for i in range(0, len(schools), 3)],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "✅ Obuna tasdiqlandi!\nEndi o‘z ovozingizni bering:",
            reply_markup=markup
        )
        return VOTE

    except Exception:
        markup = ReplyKeyboardMarkup([[KeyboardButton("✅ Obuna bo‘ldim")]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "❗️Siz hali kanalga a'zo emassiz!\n👉 https://t.me/bizbop_supermarket\n\nA'zo bo‘lib, tugmani bosing:",
            reply_markup=markup
        )
        return CHECK_SUBSCRIPTION

# Ovoz berish
async def get_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    school = update.message.text
    name = context.user_data["name"]
    phone = context.user_data["phone"]

    add_vote(name, phone, school, user_id)

    await update.message.reply_text(
        f"✅ Siz {school} uchun muvaffaqiyatli ovoz berdingiz!\n\n📊 Natijalarni quyidagi tugma orqali ko‘rishingiz mumkin:",
        reply_markup=ReplyKeyboardMarkup([["📊 Statistika"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return ConversationHandler.END

# Statistika
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chart_path = generate_stats_chart()
    with open(chart_path, "rb") as img:
        await update.message.reply_photo(img, caption="📊 Maktablar bo‘yicha ovozlar")

# Stop komandasi
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_exit(user_id)
    await update.message.reply_text("❌ Botdan chiqdingiz. Rahmat!")

# Run bot
if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN topilmadi!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            CHECK_SUBSCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_subscription_step)],
            VOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vote)],
        },
        fallbacks=[CommandHandler("stop", stop)]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("statistika", stats))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📊 Statistika$"), stats))
    app.add_handler(CommandHandler("stop", stop))

    app.run_polling()
