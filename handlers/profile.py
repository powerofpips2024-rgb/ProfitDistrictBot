from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from handlers.render import edit_or_send

ECOSYSTEM_ITEMS = [
    ("mentorship_confirmed", "30 Days Mentorship"),
    ("tg_access", "Telegram"),
    ("dc_access", "Discord"),
    ("challenge_done", "Challenge 500→5.000"),
    ("competition_done", "Competiție"),
    ("event_confirmed", "Eveniment"),
]


def _mark(active) -> str:
    return "✅" if active else "❌"


def _next_step_text(user) -> str:
    if not user["mentorship_confirmed"]:
        return "📚 Accesează mentoratul de 30 de zile"
    if not user["tg_access"]:
        return "📈 Intră în grupul de Telegram"
    if not user["dc_access"]:
        return "🔥 Intră pe Discord"
    if not user["challenge_done"]:
        return "🏆 Începe Challenge 500 → 5.000"
    if not user["competition_done"]:
        return "🥇 Înscrie-te la o competiție"
    if not user["event_confirmed"]:
        return "📅 Înscrie-te la eveniment"
    return "🎉 Ai finalizat toți pașii disponibili!"


def _ecosystem_progress(user) -> tuple[str, int, str]:
    total = len(ECOSYSTEM_ITEMS)
    done_labels = [label for field, label in ECOSYSTEM_ITEMS if user[field]]
    remaining_labels = [label for field, label in ECOSYSTEM_ITEMS if not user[field]]

    percent = round(len(done_labels) / total * 100) if total else 0
    blocks = 10
    filled = round(percent / 100 * blocks)
    bar = "█" * filled + "░" * (blocks - filled)

    if remaining_labels:
        remaining_text = "\n".join(f"⬜ {label}" for label in remaining_labels)
    else:
        remaining_text = texts.ECOSYSTEM_ALL_DONE

    return bar, percent, remaining_text


def _mission(user) -> tuple[str, str]:
    for index, (field, _) in enumerate(ECOSYSTEM_ITEMS, start=1):
        if not user[field]:
            blocks = "".join("🟩" if user[f] else "⬜" for f, _ in ECOSYSTEM_ITEMS)
            return texts.MISSION_TITLE.format(number=index), blocks
    blocks = "🟩" * len(ECOSYSTEM_ITEMS)
    return texts.MISSION_ALL_DONE_TITLE, blocks


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = db.get_user(update.effective_user.id)

    broker_line = f"{user['broker_recommended']} ✅" if user and user["broker_recommended"] else "Nesetat"
    ecosystem_bar, ecosystem_percent, ecosystem_remaining = _ecosystem_progress(user)
    mission_title, mission_progress = _mission(user)

    text = texts.PROFILE_TEMPLATE.format(
        first_name=update.effective_user.first_name or "",
        ecosystem_bar=ecosystem_bar,
        ecosystem_percent=ecosystem_percent,
        ecosystem_remaining=ecosystem_remaining,
        broker_line=broker_line,
        mentorship_mark=_mark(user["mentorship_confirmed"]),
        tg_mark=_mark(user["tg_access"]),
        dc_mark=_mark(user["dc_access"]),
        challenge_mark=_mark(user["challenge_done"]),
        competition_mark=_mark(user["competition_done"]),
        event_mark=_mark(user["event_confirmed"]),
        identity_mark=_mark(user["identity_verified"]),
        address_mark=_mark(user["address_verified"]),
        deposit_mark=_mark(user["deposit_done"]),
        mission_title=mission_title,
        mission_progress=mission_progress,
        next_step=_next_step_text(user),
        next_event=texts.NEXT_EVENT_TEXT,
    )
    await edit_or_send(query, text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")
