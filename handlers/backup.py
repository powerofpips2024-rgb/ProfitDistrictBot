from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

import db
from config import ADMIN_CHAT_ID


async def send_backup(context, chat_id):
    if not db.DB_PATH.exists():
        return
    with open(db.DB_PATH, "rb") as f:
        await context.bot.send_document(
            chat_id=chat_id,
            document=f,
            filename=f"data_{date.today().isoformat()}.db",
            caption="🗄️ Backup bază de date Profit District Bot",
        )


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_CHAT_ID or str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    await send_backup(context, update.effective_chat.id)


async def daily_backup_job(context):
    if ADMIN_CHAT_ID:
        await send_backup(context, ADMIN_CHAT_ID)
