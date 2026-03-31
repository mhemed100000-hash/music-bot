import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
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
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]
        return f"{info['id']}.mp3"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 مرحباً! أنا بوت الموسيقى\n\n"
        "/play [اسم الأغنية] — تشغيل أغنية\n"
        "/stop — إيقاف التشغيل\n"
        "/help — المساعدة"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ مثال: /play فيروز")
        return
    query = " ".join(context.args)
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(f"🔍 جاري البحث عن: {query}...")
    try:
        filename = search_youtube(query)
        await msg.edit_text(f"🎵 جاري التشغيل: {query}")
        await pytgcalls.join_group_call(chat_id, AudioPiped(filename))
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await pytgcalls.leave_group_call(update.effective_chat.id)
        await update.message.reply_text("⏹ تم إيقاف التشغيل")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 طريقة الاستخدام:\n\n"
        "١. أضفني للمجموعة كمشرف\n"
        "٢. أعطني صلاحية إدارة المكالمات\n"
        "٣. ابدأ مكالمة صوتية\n"
        "٤. اكتب /play اسم الأغنية"
    )

async def main():
    await app.start()
    await pytgcalls.start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help_cmd))
    print("✅ البوت يعمل!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
