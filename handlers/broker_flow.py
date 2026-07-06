from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from config import FP_MARKETS_LINK, PU_PRIME_LINK

PRODUCT_INTRO = {
    "tg": texts.TELEGRAM_INTRO,
    "dc": texts.DISCORD_INTRO,
    "both": texts.TELEGRAM_DISCORD_INTRO,
    "comp": texts.COMPETITION_BROKER_INTRO,
}

EXISTING_BROKER_LINK = {
    "robo": PU_PRIME_LINK,
    "multibank": FP_MARKETS_LINK,
    "fp": FP_MARKETS_LINK,
    "ic": FP_MARKETS_LINK,
    "vantage": PU_PRIME_LINK,
    "t212": PU_PRIME_LINK,
    "xtb": PU_PRIME_LINK,
    "altul": FP_MARKETS_LINK,
}

IB_IMAGE_PATH = Path(__file__).parent.parent / "assets" / "ib.jpg"


async def show_intro(update: Update, context: ContextTypes.DEFAULT_TYPE, product: str):
    query = update.callback_query
    await query.answer()
    db.update_user(update.effective_user.id, product=product)
    await query.edit_message_text(
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
        await query.edit_message_text(
            text,
            reply_markup=keyboards.onboarding_step_menu(product, step + 1, label),
            parse_mode="HTML",
        )
    elif step == 5:
        await query.edit_message_text(
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
            await query.edit_message_text(
                texts.ASK_EXISTING_BROKER,
                reply_markup=keyboards.broker_existing_menu(product),
            )
        else:
            await query.edit_message_text(
                texts.ASK_CAPITAL,
                reply_markup=keyboards.broker_capital_menu(product),
            )

    elif field == "exi":
        db.update_user(user_id, existing_broker=value)
        if value == "pu":
            db.update_user(user_id, broker_recommended="PU Prime")
            await query.edit_message_text(texts.PU_PRIME_TRANSFER_INSTRUCTIONS, parse_mode="HTML")
            with open(IB_IMAGE_PATH, "rb") as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=texts.PU_PRIME_DEPOSIT_CAPTION,
                    reply_markup=keyboards.pu_prime_continue_menu(product),
                )
            return

        link = EXISTING_BROKER_LINK[value]
        broker_name = "FP Markets" if link == FP_MARKETS_LINK else "PU Prime"
        db.update_user(user_id, broker_recommended=broker_name)
        show_support = value == "fp" and product in ("tg", "dc", "both")
        await query.edit_message_text(
            texts.RECOMMEND_FOR_EXISTING_BROKER.format(broker=broker_name),
            reply_markup=keyboards.broker_recommendation_menu(product, link, show_support=show_support),
            parse_mode="HTML",
        )

    elif field == "cap":
        db.update_user(user_id, capital=value)
        if value == "under200":
            db.update_user(user_id, broker_recommended="PU Prime")
            await query.edit_message_text(
                texts.RECOMMEND_PU_PRIME,
                reply_markup=keyboards.broker_recommendation_menu(product, PU_PRIME_LINK),
                parse_mode="HTML",
            )
        else:
            await query.edit_message_text(
                texts.ASK_PRIORITY,
                reply_markup=keyboards.broker_priority_menu(product),
            )

    elif field == "pri":
        db.update_user(user_id, priority=value)
        if value == "cost":
            broker, text = "FP Markets", texts.RECOMMEND_FP_MARKETS_COST
            link = FP_MARKETS_LINK
        elif value == "copy":
            broker, text = "FP Markets", texts.RECOMMEND_FP_MARKETS_COPY
            link = FP_MARKETS_LINK
        else:
            broker, text = "PU Prime", texts.RECOMMEND_PU_PRIME_BONUS
            link = PU_PRIME_LINK
        db.update_user(user_id, broker_recommended=broker)
        await query.edit_message_text(
            text,
            reply_markup=keyboards.broker_recommendation_menu(product, link),
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
