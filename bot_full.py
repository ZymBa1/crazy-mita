import os
import requests
import tempfile
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from gtts import gTTS

# Токены
TELEGRAM_TOKEN = os.getenv("8269598789:AAFrhPCLji4-CwJlV0E4pDI8XBNrCeVxrE4")
HF_API_KEY = os.getenv("HF_API_KEY")  # Hugging Face API Token
ADMIN_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# Шутки
jokes = [
    "Почему программисты путают Хэллоуин и Рождество? Потому что OCT 31 = DEC 25!",
    "Бот без багов? Это фантастика 😎",
    "Я – Crazy Mita, а ты?"
]

# 🎭 Hugging Face Chat (замена DeepAI)
def hf_chat(prompt: str) -> str:
    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        response = requests.post(url, headers=headers, json={"inputs": prompt})
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return "⚠️ Ошибка при обращении к Hugging Face"
    except Exception as e:
        return f"❌ Ошибка API: {e}"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, я Crazy Mita 🤖!\n"
        "Я умею отвечать на твои сообщения и даже говорить голосом.\n"
        "Команды: /help"
    )

# /help
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 Команды Crazy Mita:\n\n"
        "/start – запуск\n"
        "/help – список команд\n"
        "/voice [текст] – ответ голосом\n"
        "/ad [текст] – реклама за донат\n"
        "/joke – случайная шутка\n"
        "/quote – случайная цитата\n"
        "/quiz – мини-викторина\n"
        "/fich – предложить новую фишку\n"
        "/meme – случайный мем\n"
        "/info – инфо о пользователе\n"
        "/ping – проверка бота\n"
    )
    await update.message.reply_text(text)

# /voice
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /voice [текст]")
        return
    text = " ".join(context.args)
    reply = hf_chat(text)
    try:
        tts = gTTS(text=reply, lang="ru")
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            filename = f"{fp.name}.mp3"
            tts.save(filename)
            await update.message.reply_voice(voice=open(filename, "rb"), caption=reply)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка озвучки: {e}")

# /ad
async def ad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💸 Донатить", url="https://www.donationalerts.com/r/crazymita")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🚫 Нет! Так нельзя — нужно задонатить!\n\n#ad\n*Стоимость рекламы: 10$*"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# /joke
async def joke_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(jokes))

# /quote
async def quote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = requests.get("https://api.quotable.io/random").json()
        text = f"💬 {resp['content']} — {resp['author']}"
    except:
        text = "⚠️ Не удалось получить цитату."
    await update.message.reply_text(text)

# /quiz
quiz_questions = [
    {"question": "Сколько планет в Солнечной системе?", "answer": "8"},
    {"question": "Столица Японии?", "answer": "Токио"},
]

async def quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(quiz_questions)
    context.user_data["quiz_answer"] = q["answer"].lower()
    await update.message.reply_text(f"❓ Викторина: {q['question']}")

# /fich
async def fich_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💡 Предложить фишку", url="https://t.me/YourOtherBot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Хотите предложить новую фишку?\nЖмите кнопку 👇", reply_markup=reply_markup)

# /meme
async def meme_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        resp = requests.get("https://meme-api.com/gimme").json()
        url = resp["url"]
        await update.message.reply_photo(photo=url, caption="😂 Лови мем!")
    except:
        await update.message.reply_text("⚠️ Мемы закончились...")

# /info
async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = (
        f"👤 Твоя информация:\n\n"
        f"ID: `{user.id}`\n"
        f"Имя: {user.first_name}\n"
        f"Юзернейм: @{user.username if user.username else '—'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# /ping
async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Crazy Mita жив 🚀")

# Ответы на текст
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "quiz_answer" in context.user_data:
        if user_text.lower() == context.user_data["quiz_answer"]:
            await update.message.reply_text("✅ Верно! 🎉")
        else:
            await update.message.reply_text(f"❌ Правильный ответ: {context.user_data['quiz_answer']}")
        del context.user_data["quiz_answer"]
        return
    reply = hf_chat(user_text)
    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN or not HF_API_KEY:
        print("❌ Укажи TELEGRAM_TOKEN и HF_API_KEY в .env")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("voice", voice))
    app.add_handler(CommandHandler("ad", ad_handler))
    app.add_handler(CommandHandler("joke", joke_handler))
    app.add_handler(CommandHandler("quote", quote_handler))
    app.add_handler(CommandHandler("quiz", quiz_handler))
    app.add_handler(CommandHandler("fich", fich_handler))
    app.add_handler(CommandHandler("meme", meme_handler))
    app.add_handler(CommandHandler("info", info_handler))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ Crazy Mita запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
