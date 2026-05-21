import os
from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("BOT_TOKEN")

DELETE_AFTER = 10

PORT = int(os.environ.get("PORT", 10000))

# ======================
# FLASK WEB SERVER
# ======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Running"

def run_web():
    app.run(host="0.0.0.0", port=PORT)

# ======================
# DELETE MESSAGE
# ======================

async def delete_message(context: ContextTypes.DEFAULT_TYPE):

    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.chat_id,
            message_id=job.data
        )

        print("Deleted")

    except Exception as e:
        print(e)

# ======================
# HANDLE MESSAGE
# ======================

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    msg = update.message

    print("Message received")

    context.job_queue.run_once(
        delete_message,
        DELETE_AFTER,
        chat_id=msg.chat_id,
        data=msg.message_id,
    )

# ======================
# START BOT
# ======================

def run_bot():

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(
        MessageHandler(filters.ALL, handle)
    )

    print("Bot Started")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

# ======================
# MAIN
# ======================

if __name__ == "__main__":

    # Flask thread
    Thread(target=run_web).start()

    # Telegram bot
    run_bot()
