# =========================
# AUTO DELETE BOT FOR RENDER
# =========================

import os
import asyncio
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

BOT_TOKEN = os.getenv("BOT_TOKEN", "8821134829:AAHuzhKPMm87sakBjXrrICI9aX80ysaCAY0")

DELETE_AFTER = 10
PORT = int(os.environ.get("PORT", 10000"))

# =========================
# KEEP RENDER ALIVE
# =========================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

# =========================
# DELETE FUNCTION
# =========================

async def delete_msg(context: ContextTypes.DEFAULT_TYPE):

    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.chat_id,
            message_id=job.data
        )

        print(f"Deleted {job.data}")

    except Exception as e:
        print("Delete error:", e)

# =========================
# HANDLE ALL MSG
# =========================

async def all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.effective_message:
        return

    msg = update.effective_message

    print(f"Received message {msg.message_id}")

    # Schedule deletion
    context.job_queue.run_once(
        delete_msg,
        DELETE_AFTER,
        chat_id=msg.chat_id,
        data=msg.message_id,
    )

# =========================
# MAIN
# =========================

async def main():

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # ALL messages
    app.add_handler(
        MessageHandler(
            filters.ALL,
            all_messages
        )
    )

    print("Bot started")

    await app.initialize()
    await app.start()

    # IMPORTANT
    await app.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

    # RUN FOREVER
    while True:
        await asyncio.sleep(3600)

# =========================
# START
# =========================

if __name__ == "__main__":

    # Flask for Render
    Thread(target=run_flask).start()

    # Telegram Bot
    asyncio.run(main())
