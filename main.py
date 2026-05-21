# ==============================
# FULL FINAL AUTO DELETE BOT
# WORKS ON RENDER
# Deletes:
# - User messages
# - Bot replies
# - Other bot messages in group
# ==============================

import os
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==============================
# CONFIG
# ==============================

TOKEN = os.getenv("BOT_TOKEN")

DELETE_AFTER = 10

PORT = int(os.environ.get("PORT", 10000))

# ==============================
# FLASK SERVER
# ==============================

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot Running"

def run_web():
    web.run(host="0.0.0.0", port=PORT)

# ==============================
# DELETE FUNCTION
# ==============================

async def delete_message(context: ContextTypes.DEFAULT_TYPE):

    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.chat_id,
            message_id=job.data
        )

        print(f"Deleted message: {job.data}")

    except Exception as e:
        print(f"Delete Error: {e}")

# ==============================
# HANDLE ALL MESSAGES
# ==============================

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    msg = update.message

    print(f"Received message: {msg.message_id}")

    # ==========================
    # DELETE USER MESSAGE
    # ==========================

    context.job_queue.run_once(
        delete_message,
        DELETE_AFTER,
        chat_id=msg.chat_id,
        data=msg.message_id
    )

    # ==========================
    # DELETE OTHER BOT MESSAGES
    # ==========================

    if msg.from_user and msg.from_user.is_bot:

        context.job_queue.run_once(
            delete_message,
            DELETE_AFTER,
            chat_id=msg.chat_id,
            data=msg.message_id
        )

# ==============================
# START BOT
# ==============================

def run_bot():

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    # HANDLE ALL MESSAGES
    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle
        )
    )

    print("Bot Started Successfully")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    # Start Flask server
    Thread(target=run_web).start()

    # Start Telegram bot
    run_bot()
