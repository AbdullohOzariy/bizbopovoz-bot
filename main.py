import os
import base64
from dotenv import load_dotenv

# Load .env environment variables (Railway variables)
load_dotenv()

# Check for base64 string from env
encoded = os.environ.get("SHEETS_CREDENTIALS_JSON")
if not encoded:
    raise RuntimeError("❌ .env dagi SHEETS_CREDENTIALS_JSON topilmadi! Railway > Variables ni tekshiring.")

# Save credentials.json file
with open("credentials.json", "wb") as f:
    f.write(base64.b64decode(encoded))

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, filters, ConversationHandler
)

schools = [
    "18-maktab (shahar)",
    "10-maktab (shahar)",
    "7-maktab (shahar)",
    "20-maktab (shahar)",
    "9-maktab (shahar)",
    "4-maktab (shahar)",
    "3-maktab (shahar)",
    "5-maktab (Yo‘lchilar ovuli)",
    "12-maktab (Shalxar ovuli)"
]

user_votes = {}

NAME, PHONE, CHECK_SUBSCRIPTION, VOTE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_votes:
        await update.message.reply_text("Siz allaqachon ovoz bergansiz.")
        return ConversationHandler.END

    await update.message.reply_text(
        "👋 Assalomu alaykum! Bizbop Ovoz botiga xush kelibsiz!\n\nOvoz berish uchun avval ismingizni kiriting:"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    btn = KeyboardButton("📞 Kontakt yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Telefon raqamingizni yuboring:", reply_markup=markup)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import has_voted
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number

    if has_voted(user_id):
        await update.message.reply_text("❗️Siz allaqachon ovoz bergansiz.")
        return ConversationHandler.END

    context.user_data["phone"] = phone

    # Kanalga kirish uchun inline tugma
    inline_btn = InlineKeyboardButton("📢 Kanalga a'zo bo‘lish", url="https://t.me/BozorovPersonal")
    inline_markup = InlineKeyboardMarkup([[inline_btn]])
    await update.message.reply_text(
        "📢 Endi bizning kanalga a'zo bo‘ling:\n👇 Quyidagi tugmani bosing:",
        reply_markup=inline_markup
    )

    btn = KeyboardButton("✅ Obuna bo‘ldim")
    markup = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "✅ Obuna bo‘lib bo‘lgan bo‘lsangiz, pastdagi tugmani bosing:",
        reply_markup=markup
    )
    return CHECK_SUBSCRIPTION

async def check_subscription_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member("@BozorovPersonal", user_id)
        if member.status not in ["member", "administrator", "creator"]:
            raise Exception("Not subscribed")

        markup = ReplyKeyboardMarkup(
            [schools[i:i+3] for i in range(0, len(schools), 3)],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "✅ Obuna tasdiqlandi! Bizbop maktab maqomi uchun o‘z ovozingizni bering 👇🏼👇🏼",
            reply_markup=markup
        )
        return VOTE

    except:
        btn = KeyboardButton("✅ Obuna bo‘ldim")
        markup = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "❗️Siz hali kanalga a'zo emassiz!\n👉 https://t.me/BozorovPersonal\n\nA'zo bo‘lib, pastdagi tugmani bosing:",
            reply_markup=markup
        )
        return CHECK_SUBSCRIPTION

async def get_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import add_vote
    user_id = update.effective_user.id
    school = update.message.text
    name = context.user_data["name"]
    phone = context.user_data["phone"]

    add_vote(name, phone, school, user_id)
    user_votes[user_id] = school

    await update.message.reply_text(
        f"✅ Siz {school} uchun muvaffaqiyatli ovoz berdingiz!\n\nBiz sizning fikringizni qadrlaymiz va bunday faol ishtirokingizdan mamnunmiz.\n📊 Endi statistikani quyidagi tugma orqali kuzatib borishingiz mumkin:",
        reply_markup=ReplyKeyboardMarkup([["📊 Statistika"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import generate_stats_chart
    chart_path = generate_stats_chart()
    with open(chart_path, "rb") as img:
        await update.message.reply_photo(img, caption="📊 Maktablar bo‘yicha ovozlar")

if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN yo‘q! Railway > Variables da qo‘shing.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            CHECK_SUBSCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_subscription_step)],
            VOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vote)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("statistika", stats))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📊 Statistika$"), stats))

    app.run_polling()