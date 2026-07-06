from telegram import Update
from telegram.ext import ContextTypes

import db
from config import ADMIN_CHAT_ID
from levels import level_for_xp


TELEGRAM_MESSAGE_LIMIT = 3500


def build_xp_report() -> list[str]:
    conn = db.get_connection()
    rows = conn.execute(
        "SELECT telegram_id, username, first_name, xp FROM users ORDER BY xp DESC, telegram_id ASC"
    ).fetchall()
    conn.close()

    if not rows:
        return ["Nu există încă niciun membru înregistrat."]

    header = f"📊 <b>Evidență XP — {len(rows)} membri</b>\n"
    lines = []
    for position, row in enumerate(rows, start=1):
        name = row["first_name"] or "Utilizator"
        username = f" (@{row['username']})" if row["username"] else ""
        _, level_name, _ = level_for_xp(row["xp"])
        lines.append(f"{position}. {name}{username} — {row['xp']} XP — {level_name}")

    chunks = []
    current = header
    for line in lines:
        if len(current) + len(line) + 1 > TELEGRAM_MESSAGE_LIMIT:
            chunks.append(current)
            current = line
        else:
            current += "\n" + line
    chunks.append(current)
    return chunks


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_CHAT_ID or str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    for chunk in build_xp_report():
        await update.message.reply_text(chunk, parse_mode="HTML")
