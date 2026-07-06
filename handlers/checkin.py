from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import db
import keyboards
import texts
from handlers.render import edit_or_send

Q1, Q2, Q3, Q4, Q5, Q5_CUSTOM, Q6, Q7 = range(8)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkin"] = {}
    await query.message.reply_text(texts.CHECKIN_Q1, reply_markup=keyboards.checkin_q1_menu(), parse_mode="HTML")
    return Q1


async def q1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkin"]["analyzed_market"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKIN_Q2, reply_markup=keyboards.checkin_q2_menu())
    return Q2


async def q2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkin"]["session"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKIN_Q3, reply_markup=keyboards.checkin_q3_menu())
    return Q3


async def q3(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.split(":")[2]
    context.user_data["checkin"]["mood"] = value
    text = texts.CHECKIN_Q4
    if value in ("stressed", "tired"):
        text = f"{texts.CHECKIN_STRESS_WARNING}\n\n{texts.CHECKIN_Q4}"
    await edit_or_send(query,text, reply_markup=keyboards.checkin_q4_menu())
    return Q4


async def q4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkin"]["goal"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKIN_Q5, reply_markup=keyboards.checkin_q5_menu())
    return Q5


async def q5(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.split(":")[2]
    if value == "other":
        await edit_or_send(query,texts.CHECKIN_Q5_CUSTOM)
        return Q5_CUSTOM
    context.user_data["checkin"]["risk"] = value
    await edit_or_send(query,texts.CHECKIN_Q6, reply_markup=keyboards.checkin_q6_menu())
    return Q6


async def q5_custom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["checkin"]["risk"] = update.message.text.strip()
    await update.message.reply_text(texts.CHECKIN_Q6, reply_markup=keyboards.checkin_q6_menu())
    return Q6


async def q6(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["checkin"]["respect_plan"] = query.data.split(":")[2]
    await edit_or_send(query,texts.CHECKIN_Q7, reply_markup=keyboards.checkin_q7_menu())
    return Q7


async def q7(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    value = query.data.split(":")[2]
    context.user_data["checkin"]["checked_news"] = value

    user_id = update.effective_user.id
    already_done_today = db.checkin_exists_today(user_id)
    db.save_checkin(user_id, **context.user_data["checkin"])
    if not already_done_today:
        db.add_xp(user_id, 5)
    context.user_data.pop("checkin", None)

    text = texts.CHECKIN_DONE
    if not already_done_today:
        text += "\n\n+5 XP"
    if value == "no":
        text = f"{texts.CHECKIN_NEWS_WARNING}\n\n{text}"
    await edit_or_send(query,text)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Anulat.")
    return ConversationHandler.END


text_filter = filters.TEXT & ~filters.COMMAND
