from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from handlers.render import edit_or_send

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rows = db.get_leaderboard(10)
    user_id = update.effective_user.id

    if not rows:
        text = texts.LEADERBOARD_TITLE + texts.LEADERBOARD_EMPTY
    else:
        text = texts.LEADERBOARD_TITLE
        in_top = False
        for position, row in enumerate(rows, start=1):
            if row["telegram_id"] == user_id:
                in_top = True
            medal = MEDALS.get(position, f"{position}.")
            name = row["first_name"] or "Utilizator"
            text += texts.LEADERBOARD_ROW.format(
                medal=medal, position=position, name=name, xp=row["xp"]
            )
        if not in_top:
            rank = db.get_xp_rank(user_id)
            user = db.get_user(user_id)
            if rank and user:
                text += texts.LEADERBOARD_YOUR_RANK.format(rank=rank, xp=user["xp"])

    await edit_or_send(query, text, reply_markup=keyboards.back_to_main_menu(), parse_mode="HTML")
