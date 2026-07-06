from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from achievements import achievement_status
from handlers.render import edit_or_send
from levels import LEVELS, level_for_xp, next_level_for_xp, progress_bar, unlocked_benefits


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = db.get_user(update.effective_user.id)
    xp = user["xp"] if user else 0

    threshold, name, _ = level_for_xp(xp)
    next_level = next_level_for_xp(xp)

    if next_level is None:
        next_level_line = texts.LEVEL_MAXED_LINE
        progress_percent = 100
    else:
        next_threshold, next_name, _ = next_level
        next_level_line = texts.LEVEL_NEXT_LINE.format(
            name=next_name, threshold=next_threshold, remaining=next_threshold - xp
        )
        span = next_threshold - threshold
        progress_percent = round(((xp - threshold) / span) * 100) if span else 100

    benefits_text = "\n".join(f"• {benefit}" for benefit in unlocked_benefits(xp))

    all_levels = "\n".join(
        f"{'✅' if xp >= lvl_threshold else '🔒'} {lvl_name} ({lvl_threshold} XP)"
        for lvl_threshold, lvl_name, _ in LEVELS
    )

    streak = user["streak"] if user else 0
    streak_line = texts.STREAK_LINE.format(streak=streak) if streak else texts.STREAK_LINE_ZERO
    if streak:
        streak_line = f"🔥 {streak_line}"

    achievements_text = "\n".join(
        f"{'✅' if unlocked else '🔒'} {label}" for label, unlocked in achievement_status(user)
    )

    text = texts.LEVEL_TEMPLATE.format(
        level_name=name,
        xp=xp,
        progress_bar=progress_bar(xp),
        progress_percent=progress_percent,
        next_level_line=next_level_line,
        streak_line=streak_line,
        achievements=achievements_text,
        unlocked_benefits=benefits_text,
        all_levels=all_levels,
    )

    reply_markup = keyboards.level_menu(show_trade_button=not (user and user["first_trade_confirmed"]))
    await edit_or_send(query, text, reply_markup=reply_markup, parse_mode="HTML")
