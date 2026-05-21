import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# 🔑 Paste your BotFather token here
TOKEN = "8724187100:AAH98YncO6Bb1eQf0OM0YhgfK1JrGfnP7nE"

# ⏱️ Time before deleting (in seconds)
DELETE_AFTER = 10  # 5 horas

async def delete_later(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.delete_message(
            chat_id=job.data["chat_id"],
            message_id=job.data["message_id"]
        )
    except:
        pass

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # Detects photos, videos, or documents.
    if msg.photo or msg.video or msg.document:
        context.job_queue.run_once(
            delete_later,
            when=DELETE_AFTER,
            data={
                "chat_id": msg.chat_id,
                "message_id": msg.message_id
            }
        )

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, handle_media))

app.run_polling()
