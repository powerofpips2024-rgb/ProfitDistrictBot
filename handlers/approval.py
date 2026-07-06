from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import db
from config import ADMIN_CHAT_ID
from handlers.render import edit_or_send

DB_FIELD = {
    "mentorship": "mentorship_confirmed",
    "challenge": "challenge_done",
    "event": "event_confirmed",
    "competition": "competition_done",
    "first_trade": "first_trade_confirmed",
}

XP_AWARD = {
    "mentorship": 100,
    "challenge": 150,
    "event": 325,
    "competition": 150,
}

REQUEST_LABEL = {
    "mentorship": "finalizarea mentoratului",
    "challenge": "înscrierea la Challenge 500 → 5.000",
    "event": "participarea la eveniment",
    "competition": "înscrierea la competiție",
}

USER_MESSAGE = {
    "mentorship": "✅ Confirmat! Ai primit +100 XP pentru finalizarea mentoratului.",
    "challenge": "✅ Confirmat! Te-ai înscris la Challenge 500 → 5.000. Ai primit +150 XP.",
    "event": "✅ Confirmat! Participarea ta la eveniment a fost aprobată. Ai primit +325 XP.",
    "competition": "✅ Confirmat! Te-ai înscris la competiție. Ai primit +150 XP.",
    "first_trade": "✅ Confirmat! Ai deblocat achievement-ul 🏅 Primul Trade.",
}


async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    approval_type = query.data.split(":", 1)[1]
    user = update.effective_user

    field = DB_FIELD[approval_type]
    db_user = db.get_user(user.id)
    if db_user and db_user[field]:
        await query.answer("Ai confirmat deja.", show_alert=True)
        return

    await query.answer(
        "Cererea a fost trimisă către echipă. Vei fi notificat după confirmare.", show_alert=True
    )

    if ADMIN_CHAT_ID:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✅ Aprobă", callback_data=f"approve:{approval_type}:{user.id}")]]
        )
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔔 {user.mention_html()} (id: {user.id}) cere confirmarea pentru {REQUEST_LABEL[approval_type]}.",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not ADMIN_CHAT_ID or str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        await query.answer()
        return
    _, approval_type, user_id_str = query.data.split(":")
    user_id = int(user_id_str)

    field = DB_FIELD.get(approval_type)
    user = db.get_user(user_id)
    already_done = bool(user and field and user[field])

    if already_done:
        await query.answer("Deja aprobat.", show_alert=True)
        return

    if field:
        db.update_user(user_id, **{field: 1})
    xp = XP_AWARD.get(approval_type, 0)
    if xp:
        db.add_xp(user_id, xp)

    await query.answer("Aprobat.")
    await context.bot.send_message(chat_id=user_id, text=USER_MESSAGE.get(approval_type, "✅ Confirmat!"))

    original_text = query.message.text or query.message.caption or ""
    await edit_or_send(query, f"{original_text}\n\n✅ Aprobat.")
