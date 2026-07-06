from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from handlers.render import edit_or_send


async def show_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = db.get_user(update.effective_user.id)

    if user and not user["mentorship_started"]:
        db.update_user(user["telegram_id"], mentorship_started=1)
        db.add_xp(user["telegram_id"], 20)
        await query.answer("+20 XP! Ai deschis mentoratul.", show_alert=True)
    else:
        await query.answer()

    await edit_or_send(
        query, texts.MENTORSHIP, reply_markup=keyboards.mentorship_menu(), parse_mode="HTML"
    )
