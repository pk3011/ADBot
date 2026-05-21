# =========================
# TELEGRAM AUTO DELETE BOT
# RENDER READY
# =========================

import os
import asyncio
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

TOKEN = os.getenv("BOT_TOKEN", "8821134829:AAHuzhKPMm87sakBjXrrICI9aX80ysaCAY0")

DELETE_AFTER = 10

PORT = int(os.environ.get("PORT", 10000))

# =========================
# FLASK SERVER
# =========================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Bot Running"

def run_web():
    web_app.run(host="0.0.0.0", port=PORT)

# =========================
# DELETE FUNCTION
# =========================

async def auto_delete(context: ContextTypes.DEFAULT_TYPE):

    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )

        print(f"Deleted message {job.data['message_id']}")

    except Exception as e:
        print("Delete Error:", e)

# =========================
# HANDLE ALL MESSAGES
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    msg = update.message

    print(f"Message detected: {msg.message_id}")

    # Schedule delete
    context.job_queue.run_once(
        auto_delete,
        when=DELETE_AFTER,
        data={
            "chat_id": msg.chat_id,
            "message_id": msg.message_id
        }
    )

# =========================
# MAIN FUNCTION
# =========================

async def main():

    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    # DELETE ALL MESSAGES
    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle_message
        )
    )

    print("Bot Started")

    await app.initialize()
    await app.start()

    await app.updater.start_polling(
        allowed_updates=Update.ALL_TYPES
    )

    while True:
        await asyncio.sleep(3600)

# =========================
# START
# =========================

if __name__ == "__main__":

    Thread(target=run_web).start()

    asyncio.run(main())
