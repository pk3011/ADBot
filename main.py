# =========================
# render_bot.py
# Telegram Auto Delete Media Bot for Render
# =========================

import os
import logging
from flask import Flask
from threading import Thread

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

TOKEN = os.getenv("BOT_TOKEN", "8821134829:AAHuzhKPMm87sakBjXrrICI9aX80ysaCAY0")

# Auto delete time (seconds)
DELETE_AFTER = 10

# Render uses PORT env
PORT = int(os.environ.get("PORT", 10000))

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# KEEP ALIVE WEB SERVER
# =========================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    flask_app.run(host="0.0.0.0", port=PORT)

# =========================
# DELETE FUNCTION
# =========================

async def delete_later(context: ContextTypes.DEFAULT_TYPE):
    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )
    except Exception as e:
        print(f"Delete error: {e}")

# =========================
# HANDLE MEDIA
# =========================

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if not msg:
        return

    # Detect photos, videos, documents
    if msg.photo or msg.video or msg.document:

        context.job_queue.run_once(
            delete_later,
            when=DELETE_AFTER,
            data={
                "chat_id": msg.chat_id,
                "message_id": msg.message_id
            }
        )

# =========================
# MAIN BOT
# =========================

async def main():
    app = Application.builder().token(TOKEN).build()

    # All media messages
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.Document.ALL,
            handle_media
        )
    )

    print("Bot started successfully...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Run forever
    while True:
        await asyncio.sleep(3600)

# =========================
# START EVERYTHING
# =========================

if __name__ == "__main__":

    # Start Flask server for Render
    Thread(target=run_web).start()

    # Start Telegram bot
    asyncio.run(main())
