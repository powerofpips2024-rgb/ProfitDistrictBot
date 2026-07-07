import html

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
        name = html.escape(row["first_name"] or "Utilizator")
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


def build_pending_report() -> str | None:
    """Members whose XP was queued (via /setxp) because they weren't found in
    the database yet -- invisible in build_xp_report() since they don't exist
    in the users table. Their XP applies automatically the moment they send
    /start again; until then, this is the only way to see who's still owed."""
    rows = db.list_pending_xp()
    if not rows:
        return None
    lines = [f"⏳ <b>În așteptare — {len(rows)} membri</b>", "(XP-ul li se aplică automat la următorul /start)\n"]
    for row in rows:
        name = html.escape(row["first_name"] or "Utilizator")
        username = f" (@{html.escape(row['username'])})" if row["username"] else ""
        lines.append(f"{name}{username} — {row['xp']} XP")
    return "\n".join(lines)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_CHAT_ID or str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    for chunk in build_xp_report():
        await update.message.reply_text(chunk, parse_mode="HTML")
    pending = build_pending_report()
    if pending:
        await update.message.reply_text(pending, parse_mode="HTML")
