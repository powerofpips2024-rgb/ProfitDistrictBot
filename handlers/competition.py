import html
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import keyboards
import texts
from config import ADMIN_CHAT_ID
from handlers.render import edit_or_send

logger = logging.getLogger(__name__)

MYFXBOOK_LINK = 0


async def show_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await edit_or_send(
        query, texts.COMPETITIONS_INTRO, reply_markup=keyboards.competitions_intro_menu(), parse_mode="HTML"
    )


async def route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    step = int(query.data.split(":")[2])

    if step == 3:
        await edit_or_send(
            query, texts.COMPETITION_STEP_3, reply_markup=keyboards.competition_step3_menu(), parse_mode="HTML"
        )


async def ask_myfxbook_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await edit_or_send(
        query, texts.COMPETITION_STEP_4, reply_markup=keyboards.back_to_main_menu(), parse_mode="HTML"
    )
    return MYFXBOOK_LINK


async def receive_myfxbook_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    link = update.message.text.strip()
    if not link.lower().startswith("http"):
        await update.message.reply_text(texts.INVALID_MYFXBOOK_LINK)
        return MYFXBOOK_LINK

    user = update.effective_user
    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🔔 Link Myfxbook primit de la {user.mention_html()} (id: {user.id}):\n{html.escape(link)}",
                parse_mode="HTML",
            )
        except Exception:
            # A failure to notify the admin must never block the user's own
            # success message below.
            logger.exception("Nu am putut notifica adminul despre linkul Myfxbook al lui %s", user.id)

    await update.message.reply_text(
        texts.COMPETITION_SUCCESS, reply_markup=keyboards.competition_success_menu(), parse_mode="HTML"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Am anulat. Poți relua oricând din meniul principal.",
        reply_markup=keyboards.back_to_main_menu(),
    )
    return ConversationHandler.END


text_filter = filters.TEXT & ~filters.COMMAND
