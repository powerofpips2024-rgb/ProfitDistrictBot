from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import db
import texts
from config import ADMIN_CHAT_ID

PHOTO = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = db.get_user(update.effective_user.id)
    if user and user["first_trade_confirmed"]:
        await query.answer("Ai deblocat deja acest achievement.", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    await query.message.reply_text(texts.FIRST_TRADE_ASK_PHOTO)
    return PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    if not message.photo:
        await message.reply_text(texts.FIRST_TRADE_INVALID_PHOTO)
        return PHOTO

    user = update.effective_user
    photo_file_id = message.photo[-1].file_id

    await message.reply_text(texts.FIRST_TRADE_SENT)

    if ADMIN_CHAT_ID:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Aprobă", callback_data=f"approve:first_trade:{user.id}")]]
        )
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=photo_file_id,
            caption=f"🔔 {user.mention_html()} (id: {user.id}) cere achievement-ul Primul Trade.",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Anulat.")
    return ConversationHandler.END


photo_filter = filters.PHOTO
