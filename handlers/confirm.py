from telegram import Update
from telegram.ext import ContextTypes

import db

TOAST = {
    "tg_access": "✅ Perfect! Te așteptăm în grupul de Telegram.",
    "dc_access": "✅ Perfect! Te așteptăm pe Discord.",
    "tgdc_access": "✅ Perfect! Te așteptăm în Telegram și pe Discord.",
}

XP_AWARD = {
    "tg_access": 50,
    "dc_access": 50,
    "tgdc_access": 100,
}


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    field = query.data.split(":", 1)[1]
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if field == "tgdc_access":
        already_done = bool(user and user["tg_access"] and user["dc_access"])
        db.update_user(user_id, tg_access=1, dc_access=1)
    else:
        already_done = bool(user and user[field])
        db.update_user(user_id, **{field: 1})

    xp = XP_AWARD.get(field, 0)
    toast = TOAST.get(field, "✅ Confirmat!")
    if xp and not already_done:
        db.add_xp(user_id, xp)
        toast += f" (+{xp} XP)"
    await query.answer(toast, show_alert=True)
