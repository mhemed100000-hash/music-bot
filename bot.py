import os
import yt_dlp
import imageio_ffmpeg
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")

def search_youtube(query, download=False):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "ffmpeg_location": ffmpeg_path,
    }
    if download:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=download)
        if "entries" in info:
            info = info["entries"][0]
        if download:
            return f"/tmp/{info['id']}.mp3", info['title']
        return info["webpage_url"], info['title']

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.startswith("شغل "):
        query = text[4:].strip()
        msg = await update.message.reply_text(f"🔍 جاري البحث عن: {query}...")
        try:
            url, title = search_youtube(query)
            await msg.edit_text(f"🎵 {title}\n\n{url}")
        except Exception as e:
            await msg.edit_text(f"❌ خطأ: {str(e)}")
    elif text.startswith("يوت "):
        query = text[4:].strip()
        msg = await update.message.reply_text(f"⬇️ جاري تحميل: {query}...")
        try:
            filepath, title = search_youtube(query, download=True)
            await msg.edit_text(f"📤 جاري الإرسال: {title}")
            with open(filepath, "rb") as f:
                await update.message.reply_audio(audio=f, title=title)
            await msg.delete()
            os.remove(filepath)
        except Exception as e:
            await msg.edit_text(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ البوت يعمل!")
    application.run_polling()
