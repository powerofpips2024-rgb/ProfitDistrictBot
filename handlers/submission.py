import html
import re

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters

import db
import keyboards
import texts
from config import ADMIN_CHAT_ID
from handlers.render import edit_or_send

NUME, PRENUME, EMAIL, DISCORD_USERNAME, PROOF = range(5)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ACCESS_TEXT = {
    "tg": texts.TELEGRAM_ACCESS_GRANTED,
    "dc": texts.DISCORD_ACCESS_GRANTED,
    "both": texts.BOTH_ACCESS_GRANTED,
}


async def start_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, product, variant, _ = query.data.split(":")
    context.user_data["submission_product"] = product
    context.user_data["submission_variant"] = variant
    context.user_data.pop("email", None)
    context.user_data.pop("discord_username", None)
    await edit_or_send(query, texts.ASK_NUME)
    return NUME


async def receive_nume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["nume"] = update.message.text.strip()
    await update.message.reply_text(texts.ASK_PRENUME)
    return PRENUME


async def receive_prenume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["prenume"] = update.message.text.strip()
    if context.user_data.get("submission_variant") == "pu":
        return await _after_prenume_or_email(update, context)
    await update.message.reply_text(texts.ASK_EMAIL)
    return EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text.strip()
    if not EMAIL_RE.match(email):
        await update.message.reply_text(texts.INVALID_EMAIL)
        return EMAIL
    context.user_data["email"] = email
    return await _after_prenume_or_email(update, context)


async def _after_prenume_or_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    product = context.user_data["submission_product"]
    if product in ("dc", "both"):
        await update.message.reply_text(texts.ASK_DISCORD_USERNAME_FIELD)
        return DISCORD_USERNAME
    await update.message.reply_text(texts.ASK_PROOF)
    return PROOF


async def receive_discord_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["discord_username"] = update.message.text.strip()
    await update.message.reply_text(texts.ASK_PROOF)
    return PROOF


async def receive_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    if message.photo:
        proof_file_id = message.photo[-1].file_id
    elif message.document:
        proof_file_id = message.document.file_id
    else:
        await message.reply_text(texts.INVALID_PROOF)
        return PROOF

    user = update.effective_user
    product = context.user_data["submission_product"]
    nume = context.user_data["nume"]
    prenume = context.user_data["prenume"]
    email = context.user_data.get("email")
    discord_username = context.user_data.get("discord_username")

    db.update_user(
        user.id,
        nume=nume,
        prenume=prenume,
        email=email,
        discord_username=discord_username,
        proof_file_id=proof_file_id,
        access_granted=1,
    )

    await _notify_admin_submission(context, user, product, nume, prenume, email, discord_username)

    if product == "comp":
        await message.reply_text(
            texts.COMPETITION_STEP_2, reply_markup=keyboards.competition_step2_menu(), parse_mode="HTML"
        )
    else:
        await message.reply_text(ACCESS_TEXT[product], reply_markup=keyboards.access_link_menu(product))
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Înscrierea a fost anulată. Poți relua oricând din meniul principal.",
        reply_markup=keyboards.back_to_main_menu(),
    )
    return ConversationHandler.END


PRODUCT_LABEL = {"tg": "Telegram", "dc": "Discord", "both": "Telegram + Discord", "comp": "Competiție"}


async def _notify_admin_submission(context, user, product, nume, prenume, email, discord_username):
    if not ADMIN_CHAT_ID:
        return
    db_user = db.get_user(user.id)
    broker = db_user["broker_recommended"] if db_user else "-"
    text = texts.ADMIN_NOTIFICATION.format(
        product=PRODUCT_LABEL[product],
        mention=user.mention_html(),
        telegram_id=user.id,
        nume=html.escape(nume),
        prenume=html.escape(prenume),
        email=html.escape(email) if email else "-",
        broker=broker,
    )
    if discord_username:
        text += f"\nUsername Discord: {html.escape(discord_username)}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="HTML")
    proof_file_id = db_user["proof_file_id"] if db_user else None
    if proof_file_id:
        try:
            await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=proof_file_id)
        except Exception:
            await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=proof_file_id)


text_filter = filters.TEXT & ~filters.COMMAND
proof_filter = filters.PHOTO | filters.Document.ALL
