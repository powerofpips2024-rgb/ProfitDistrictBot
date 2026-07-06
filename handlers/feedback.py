import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import db
import keyboards
import texts
from config import ADMIN_CHAT_ID

logger = logging.getLogger(__name__)

PHOTO = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(texts.FEEDBACK_ASK_PHOTO, parse_mode="HTML")
    return PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    if not message.photo:
        await message.reply_text(texts.FEEDBACK_INVALID_PHOTO)
        return PHOTO

    user = update.effective_user
    awarded = db.record_daily_feedback(user.id)

    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=f"📸 Feedback zilnic de la {user.mention_html()} (id: {user.id}).",
                parse_mode="HTML",
            )
        except Exception:
            # A failure to notify the admin must never block the user's own
            # confirmation below -- their XP was already recorded above.
            logger.exception("Nu am putut notifica adminul despre feedback-ul lui %s", user.id)

    if awarded:
        await message.reply_text(texts.FEEDBACK_RECEIVED, reply_markup=keyboards.back_to_main_menu())
    else:
        await message.reply_text(texts.FEEDBACK_XP_ALREADY_TODAY, reply_markup=keyboards.back_to_main_menu())
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Anulat.")
    return ConversationHandler.END


photo_filter = filters.PHOTO
