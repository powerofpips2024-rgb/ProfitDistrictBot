import re

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import db
from config import ADMIN_CHAT_ID

WAITING = 0

LINE_RE = re.compile(r"^\s*\d+\.\s+(.+?)(?:\s*\(@(\w+)\))?\s*[—-]\s*(\d+)\s*XP", re.MULTILINE)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not ADMIN_CHAT_ID or str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return ConversationHandler.END
    await update.message.reply_text(
        "Lipește lista cu membri și XP (formatul din /raport, ex: \"1. Nume (@username) — 815 XP — 🔥 Consistent\")."
    )
    return WAITING


async def receive_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    matches = LINE_RE.findall(text)
    if not matches:
        await update.message.reply_text("Nu am găsit nicio linie validă. Anulat.")
        return ConversationHandler.END

    updated = []
    queued = []
    for name, username, xp_text in matches:
        name = name.strip()
        xp = int(xp_text)
        row = db.find_user_by_username(username) if username else None
        if row is None:
            row = db.find_user_by_first_name(name)
        if row is None:
            label = f"{name} (@{username})" if username else name
            db.queue_pending_xp(username, name, xp)
            queued.append(label)
        else:
            db.update_user(row["telegram_id"], xp=xp)
            updated.append(name)

    summary = f"✅ XP actualizat pentru {len(updated)} membri."
    if queued:
        summary += (
            f"\n\n⏳ Puși în așteptare ({len(queued)}) — nu sunt încă în baza de date, "
            "dar XP-ul li se va aplica automat de îndată ce trimit /start botului, "
            "fără să reia nimic de la capăt:\n"
        )
        summary += "\n".join(queued)
    await update.message.reply_text(summary)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Anulat.")
    return ConversationHandler.END


text_filter = filters.TEXT & ~filters.COMMAND
