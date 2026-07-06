from telegram import Update
from telegram.ext import ContextTypes

import keyboards
import texts


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        texts.CONTACT_TEXT, reply_markup=keyboards.back_to_main_menu(), parse_mode="HTML"
    )
