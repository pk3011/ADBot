import os
from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

DELETE_AFTER = 10

PORT = int(os.environ.get("PORT", 10000))

# ======================
# FLASK
# ======================

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot Running"

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

# ======================
# DELETE FUNCTION
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
# BOT
# ======================

def run_bot():

    application = (
        Application.builder()
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

    Thread(target=run_web).start()

    run_bot()
