from telegram import Update
from telegram.ext import ContextTypes

import keyboards
import texts
from handlers.render import edit_or_send


async def show_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"{texts.CHALLENGE_INTRO}\n\n{texts.CHALLENGE_STEP_1}"
    await edit_or_send(query, text, reply_markup=keyboards.challenge_menu(), parse_mode="HTML")


async def route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    step = int(query.data.split(":")[2])

    if step == 2:
        await edit_or_send(
            query,
            texts.CHALLENGE_BONUS_INFO,
            reply_markup=keyboards.challenge_step_menu("chl:step:3", "➡️ Continuă"),
            parse_mode="HTML",
        )
    elif step == 3:
        await edit_or_send(
            query,
            texts.CHALLENGE_STEP_2,
            reply_markup=keyboards.challenge_step_menu("chl:step:4", "✅ Am depus"),
            parse_mode="HTML",
        )
    elif step == 4:
        await edit_or_send(
            query,
            texts.CHALLENGE_STEP_3,
            reply_markup=keyboards.challenge_success_menu(),
            parse_mode="HTML",
        )
