from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from config import FP_MARKETS_LINK
from handlers.render import edit_or_send

PRODUCT_INTRO = {
    "tg": texts.TELEGRAM_INTRO,
    "dc": texts.DISCORD_INTRO,
    "both": texts.TELEGRAM_DISCORD_INTRO,
    "comp": texts.COMPETITION_BROKER_INTRO,
}


async def show_intro(update: Update, context: ContextTypes.DEFAULT_TYPE, product: str):
    query = update.callback_query
    await query.answer()
    db.update_user(update.effective_user.id, product=product)
    await edit_or_send(
        query,
        PRODUCT_INTRO[product],
        reply_markup=keyboards.broker_has_broker_menu(product),
        parse_mode="HTML",
    )


async def _show_onboarding_step(update: Update, product: str, step: int):
    query = update.callback_query
    step_content = {
        1: (texts.ONBOARDING_STEP_1, "✅ Am creat cont"),
        2: (texts.ONBOARDING_STEP_2, "✅ Am verificat identitatea"),
        3: (texts.ONBOARDING_STEP_3, "✅ Am verificat adresa"),
        4: (texts.ONBOARDING_STEP_4, "✅ Am depus"),
    }
    if step in step_content:
        text, label = step_content[step]
        await edit_or_send(
            query,
            text,
            reply_markup=keyboards.onboarding_step_menu(product, step + 1, label),
            parse_mode="HTML",
        )
    elif step == 5:
        await edit_or_send(
            query,
            texts.ONBOARDING_STEP_5,
            reply_markup=keyboards.submission_start_menu(product),
            parse_mode="HTML",
        )


async def route_broker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product, field, value = query.data.split(":")
    user_id = update.effective_user.id

    if field == "has":
        db.update_user(user_id, has_broker=value)
        if value == "yes":
            await edit_or_send(
                query,
                texts.ASK_EXISTING_BROKER,
                reply_markup=keyboards.broker_existing_menu(product),
            )
            return
    elif field == "exi":
        db.update_user(user_id, existing_broker=value)

    # Recomandam doar FP Markets. Butoanele vechi (PU Prime, capital, prioritate)
    # ramase in chat-uri mai vechi ajung tot aici, in loc sa nu mai raspunda.
    db.update_user(user_id, broker_recommended="FP Markets")
    if field == "exi":
        text = texts.RECOMMEND_FOR_EXISTING_BROKER.format(broker="FP Markets")
    else:
        text = texts.RECOMMEND_FP_MARKETS
    show_support = field == "exi" and value == "fp" and product in ("tg", "dc", "both")
    await edit_or_send(
        query,
        text,
        reply_markup=keyboards.broker_recommendation_menu(product, FP_MARKETS_LINK, show_support=show_support),
        parse_mode="HTML",
    )


async def route_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, product, _, step = query.data.split(":")
    step = int(step)
    user_id = update.effective_user.id

    if step == 3:
        db.update_user(user_id, identity_verified=1)
    elif step == 4:
        db.update_user(user_id, address_verified=1)
    elif step == 5:
        db.update_user(user_id, deposit_done=1)

    await _show_onboarding_step(update, product, step)
