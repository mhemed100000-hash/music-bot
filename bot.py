import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def search_youtube(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["webpage_url"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 مرحباً! أنا بوت الموسيقى\n"
        "/play اسم الأغنية — للبحث عن رابط\n"
        "/help — المساعدة"
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ مثال: /play فيروز")
        return
    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 جاري البحث عن: {query}...")
    try:
        url = search_youtube(query)
        await msg.edit_text(f"🎵 وجدت الأغنية:\n{url}")
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 اكتب /play واسم الأغنية\n"
        "مثال: /play ام كلثوم"
    )

if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("help", help_cmd))
    print("✅ البوت يعمل!")
    application.run_polling()
