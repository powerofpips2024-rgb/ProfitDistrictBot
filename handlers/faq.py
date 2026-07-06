from telegram import Update
from telegram.ext import ContextTypes

import keyboards
import texts


async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "❓ <b>Întrebări frecvente</b>\n\nAlege o întrebare 👇",
        reply_markup=keyboards.faq_list_menu(),
        parse_mode="HTML",
    )


async def show_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    index = int(query.data.split(":")[1])
    question, answer = texts.FAQ_LIST[index]
    text = f"❓ <b>{question}</b>\n\n{answer}"
    await query.edit_message_text(text, reply_markup=keyboards.faq_answer_menu(), parse_mode="HTML")
