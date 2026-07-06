from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import db
import keyboards
import texts
from handlers.render import edit_or_send

Q1, Q2, Q3, Q4_TEXT, Q5_TEXT, Q6 = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkout"] = {}
    await query.message.reply_text(texts.CHECKOUT_Q1, reply_markup=keyboards.checkout_q1_menu(), parse_mode="HTML")
    return Q1


async def q1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkout"]["traded"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKOUT_Q2, reply_markup=keyboards.checkout_q2_menu())
    return Q2


async def q2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkout"]["respected_plan"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKOUT_Q3, reply_markup=keyboards.checkout_q3_menu())
    return Q3


async def q3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkout"]["day_feeling"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKOUT_Q4)
    return Q4_TEXT


async def q4_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["checkout"]["learned_text"] = update.message.text.strip()
    await update.message.reply_text(texts.CHECKOUT_Q5)
    return Q5_TEXT


async def q5_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["checkout"]["improve_text"] = update.message.text.strip()
    await update.message.reply_text(texts.CHECKOUT_Q6, reply_markup=keyboards.checkout_q6_menu())
    return Q6


async def q6(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkout"]["identity_answer"] = query.data.split(":")[2]

    db.save_checkout(update.effective_user.id, **context.user_data["checkout"])
    context.user_data.pop("checkout", None)

    await edit_or_send(query,texts.CHECKOUT_DONE)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Anulat.")
    return ConversationHandler.END


text_filter = filters.TEXT & ~filters.COMMAND
