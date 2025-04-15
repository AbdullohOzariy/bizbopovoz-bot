import os, base64

# Faylni doim yozib qo‘yamiz
with open("credentials.json", "wb") as f:
    f.write(base64.b64decode(os.environ["SHEETS_CREDENTIALS_JSON"]))

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

# 🧠 Sheets importni pasroqda qilamiz (kechiktirib)
# FUNKSIYALARNING ichida import qilamiz

schools = [f"Maktab {i}" for i in range(1, 10)]
user_votes = {}

NAME, SURNAME, PHONE, VOTE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import has_voted  # kechiktirilgan import
    user_id = update.effective_user.id

    is_subscribed = await check_subscription(update, context)
    if not is_subscribed:
        await update.message.reply_text("❗️Avval kanalga a’zo bo‘ling: https://t.me/bizbop_ovoz")
        return ConversationHandler.END

    if user_id in user_votes:
        await update.message.reply_text("Siz allaqachon ovoz bergansiz.")
        return ConversationHandler.END

    await update.message.reply_text("Ismingizni kiriting:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Familiyangizni kiriting:")
    return SURNAME

async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["surname"] = update.message.text
    btn = KeyboardButton("📞 Kontakt yuborish", request_contact=True)
    markup = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Telefon raqamingizni yuboring:", reply_markup=markup)
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import has_voted
    phone = update.message.contact.phone_number
    if has_voted(phone):
        await update.message.reply_text("Siz allaqachon ovoz bergansiz.")
        return ConversationHandler.END

    context.user_data["phone"] = phone
    markup = ReplyKeyboardMarkup([[s] for s in schools], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Qaysi maktabga ovoz bermoqchisiz?", reply_markup=markup)
    return VOTE

async def get_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import add_vote
    user_id = update.effective_user.id
    school = update.message.text
    name = context.user_data["name"]
    surname = context.user_data["surname"]
    phone = context.user_data["phone"]

    add_vote(name, surname, phone, school)
    user_votes[user_id] = school
    await update.message.reply_text(f"{school} uchun ovoz berdingiz ✅")
    return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from sheets import get_stats
    s = get_stats()
    text = "📊 Statistikalar:\n\n" + "\n".join(f"{k}: {v} ta" for k, v in s.items())
    await update.message.reply_text(text)

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member("@bizbop_ovoz", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            VOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_vote)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("statistika", stats))
    app.run_polling()
