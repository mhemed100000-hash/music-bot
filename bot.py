import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pyrogram import Client

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH)
pytgcalls = PyTgCalls(app)

def search_youtube(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 مرحباً!\n/play اسم الأغنية — تشغيل\n/stop — إيقاف"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ مثال: /play فيروز")
        return
    query = " ".join(context.args)
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(f"🔍 جاري البحث عن: {query}...")
    try:
        url = search_youtube(query)
        await pytgcalls.join_group_call(chat_id, MediaStream(url))
        await msg.edit_text(f"🎵 يشتغل الآن: {query}")
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await pytgcalls.leave_group_call(update.effective_chat.id)
        await update.message.reply_text("⏹ توقف")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def main():
    await app.start()
    await pytgcalls.start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("stop", stop))
    print("✅ البوت يعمل!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
