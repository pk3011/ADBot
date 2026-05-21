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

BOT_TOKEN = os.getenv("BOT_TOKEN")

DELETE_AFTER = 10

PORT = int(os.environ.get("PORT", 10000))

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot running"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

# Delete function
async def delete_msg(context: ContextTypes.DEFAULT_TYPE):

    job = context.job

    try:
        await context.bot.delete_message(
            chat_id=job.chat_id,
            message_id=job.data
        )

        print("Deleted")

    except Exception as e:
        print(e)

# Handle messages
async def all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    msg = update.message

    context.job_queue.run_once(
        delete_msg,
        DELETE_AFTER,
        chat_id=msg.chat_id,
        data=msg.message_id,
    )

# Main
async def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.ALL, all_messages)
    )

    await app.initialize()
    await app.start()

    await app.updater.start_polling()

    print("Bot started")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":

    Thread(target=run_flask).start()

    asyncio.run(main())
