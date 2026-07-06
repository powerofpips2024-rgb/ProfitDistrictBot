from telegram import Update
from telegram.ext import ContextTypes

import db
import keyboards
import texts
from handlers import broker_flow, challenge, competition, contact, faq, leaderboard, level, mentorship, profile
from handlers.render import edit_or_send


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, user.username, user.first_name)
    restored_xp = db.claim_pending_xp(user.id, user.username, user.first_name)
    if restored_xp is not None:
        await update.message.reply_text(
            f"🎉 Am recuperat progresul tău anterior: {restored_xp} XP!"
        )
    await update.message.reply_text(
        texts.WELCOME, reply_markup=keyboards.main_menu(db.get_user(user.id)), parse_mode="HTML"
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await edit_or_send(
        query,
        texts.WELCOME,
        reply_markup=keyboards.main_menu(db.get_user(update.effective_user.id)),
        parse_mode="HTML",
    )


async def show_start_here(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        texts.START_HERE, reply_markup=keyboards.start_here_menu(), parse_mode="HTML"
    )


async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        texts.EVENTS_TEXT, reply_markup=keyboards.events_menu(), parse_mode="HTML"
    )


async def show_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        texts.RESOURCES_TEXT, reply_markup=keyboards.back_to_main_menu(), parse_mode="HTML"
    )


async def route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = update.callback_query.data.split(":", 1)[1]

    if action == "telegram":
        await broker_flow.show_intro(update, context, "tg")
        return
    if action == "discord":
        await broker_flow.show_intro(update, context, "dc")
        return
    if action == "tgdc":
        await broker_flow.show_intro(update, context, "both")
        return
    if action == "comp_join":
        await broker_flow.show_intro(update, context, "comp")
        return

    handlers_map = {
        "main": show_main_menu,
        "start": show_start_here,
        "competitions": competition.show_intro,
        "events": show_events,
        "resources": show_resources,
        "mentorship": mentorship.show_intro,
        "challenge": challenge.show_intro,
        "faq": faq.show_list,
        "contact": contact.show,
        "profile": profile.show,
        "level": level.show,
        "leaderboard": leaderboard.show,
    }
    handler = handlers_map.get(action)
    if handler:
        await handler(update, context)
