from telegram import Update
from telegram.ext import ContextTypes

import db
from config import ADMIN_CHAT_ID
from levels import level_for_xp


def build_xp_report() -> str:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT telegram_id, username, first_name, xp FROM users ORDER BY xp DESC, telegram_id ASC"
    ).fetchall()
    conn.close()

    if not rows:
        return "Nu există încă niciun membru înregistrat."

    lines = [f"📊 <b>Evidență XP — {len(rows)} membri</b>\n"]
    for position, row in enumerate(rows, start=1):
        name = row["first_name"] or "Utilizator"
        username = f" (@{row['username']})" if row["username"] else ""
        _, level_name, _ = level_for_xp(row["xp"])
        lines.append(f"{position}. {name}{username} — {row['xp']} XP — {level_name}")

    return "\n".join(lines)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_CHAT_ID or str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    await update.message.reply_text(build_xp_report(), parse_mode="HTML")
