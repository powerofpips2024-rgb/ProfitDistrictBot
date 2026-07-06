import logging

from telegram import Update
from telegram.ext import ContextTypes

import texts

logger = logging.getLogger(__name__)


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    try:
        await context.bot.send_message(chat_id=request.from_user.id, text=texts.GROUP_WELCOME_TEXT)
    except Exception:
        logger.warning("Nu am putut trimite mesajul de bun venit către %s", request.from_user.id)
    await request.approve()
