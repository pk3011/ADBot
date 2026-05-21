# =========================
# render_bot.py
# AUTO DELETE MEDIA BOT
# WORKS IN GROUPS + PRIVATE
# =========================

import os
import asyncio
import logging
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN", "8821134829:8821134829:AAHuzhKPMm87sakBjXrrICI9aX80ysaCAY0")

# Delete after seconds
DELETE_AFTER = 10

PORT = int(os.environ.get("PORT", 10000))

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# KEEP RENDER ALIVE
# =========================

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot Running Successfully"

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

# =========================
# DELETE MESSAGE
# =========================

async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )
        print(f"Deleted: {job.data['message_id']}")

    except Exception as e:
        print(f"Delete failed: {e}")

# =========================
# HANDLE MEDIA
# =========================

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    msg = update.message

    # Detect media
    if (
        msg.photo
        or msg.video
        or msg.document
        or msg.animation
        or msg.audio
        or msg.voice
        or msg.video_note
    ):

        print(f"Media detected in chat {msg.chat_id}")

        context.job_queue.run_once(
            delete_message,
            when=DELETE_AFTER,
            data={
                "chat_id": msg.chat_id,
                "message_id": msg.message_id
            }
        )

# =========================
# MAIN
# =========================

async def main():

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # ALL MEDIA TYPES
    media_filter = (
        filters.PHOTO
        | filters.VIDEO
        | filters.Document.ALL
        | filters.AUDIO
        | filters.VOICE
        | filters.ANIMATION
        | filters.VIDEO_NOTE
    )

    application.add_handler(
        MessageHandler(media_filter, handle_media)
    )

    print("Bot Started...")

    await application.initialize()
    await application.start()
    await application.updater.start_polling(
        allowed_updates=Update.ALL_TYPES
    )

    while True:
        await asyncio.sleep(3600)

# =========================
# START
# =========================

if __name__ == "__main__":

    # Flask thread
    Thread(target=run_web).start()

    # Telegram bot
    asyncio.run(main())
