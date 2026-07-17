import datetime
import logging
from zoneinfo import ZoneInfo

from telegram import BotCommand, BotCommandScopeChat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Forbidden
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

import db
import texts
from config import ADMIN_CHAT_ID, BOT_TOKEN
from handlers import (
    approval,
    backup,
    broker_flow,
    challenge,
    checkin,
    checkout,
    competition,
    confirm,
    faq,
    feedback,
    join,
    menu,
    report,
    setxp,
    submission,
    trade,
)

TIMEZONE = ZoneInfo("Europe/Bucharest")

# PTB's day-of-week convention for JobQueue.run_daily is 0=Sunday..6=Saturday.
# Piața e închisă sâmbătă și duminică, deci mesajele zilnice automate rulează
# doar luni-vineri până se adaugă un mesaj dedicat pentru weekend.
WEEKDAYS_MON_FRI = (1, 2, 3, 4, 5)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def _daily_bonus(update, context):
    user = update.effective_user
    if user:
        db.award_daily_bonus(user.id)


async def _broadcast(context, text, reply_markup):
    for telegram_id in db.all_telegram_ids():
        try:
            await context.bot.send_message(chat_id=telegram_id, text=text, reply_markup=reply_markup)
        except Forbidden:
            continue
        except Exception:
            logger.exception("Nu am putut trimite mesajul programat către %s", telegram_id)


async def _send_daily_reminder(context):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📸 Trimite feedback", callback_data="feedback:start")]]
    )
    await _broadcast(context, texts.DAILY_REMINDER_TEXT, keyboard)


async def _send_checkin_prompt(context):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(texts.CHECKIN_START_BUTTON, callback_data="checkin:start")]]
    )
    await _broadcast(context, texts.CHECKIN_MORNING_PROMPT, keyboard)


async def _send_checkout_prompt(context):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(texts.CHECKOUT_START_BUTTON, callback_data="checkout:start")]]
    )
    await _broadcast(context, texts.CHECKOUT_EVENING_PROMPT, keyboard)


async def _restart_from_stuck_conversation(update, context):
    """Fallback for every ConversationHandler: if a user is stuck mid-flow (e.g. an
    abandoned text prompt) and sends /start, cancel that flow and show the main menu
    instead of silently ignoring the command or, worse, having an unrelated
    conversation swallow their next message."""
    await menu.start_command(update, context)
    return ConversationHandler.END


HINT_NEEDS_TEXT = "✏️ Te rog scrie un răspuns text ca să continui (sau /cancel ca să renunți)."
HINT_NEEDS_PHOTO = "📎 Te rog trimite o poză (sau document) ca să continui (sau /cancel ca să renunți)."
HINT_NEEDS_BUTTON = "👆 Te rog apasă unul din butoanele de mai sus ca să continui."


async def _hint_needs_text(update, context):
    """Catch-all appended to every text-only conversation state: if the user sends a
    photo/sticker/voice/etc. instead of typing, respond with a hint instead of silently
    ignoring the message (which otherwise looks exactly like a broken button)."""
    await update.message.reply_text(HINT_NEEDS_TEXT)
    return None


async def _hint_needs_photo(update, context):
    """Same idea as _hint_needs_text, for states that expect a photo/document."""
    await update.message.reply_text(HINT_NEEDS_PHOTO)
    return None


async def _hint_needs_button(update, context):
    """Catch-all appended to callback-button conversation states: if the user types
    text instead of tapping a button, respond with a hint instead of silence."""
    await update.message.reply_text(HINT_NEEDS_BUTTON)
    return None


async def error_handler(update, context):
    if isinstance(context.error, BadRequest) and "Message is not modified" in str(context.error):
        return
    logger.error("Unhandled exception while processing update %s", update, exc_info=context.error)


async def _post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [BotCommand("start", "Pornește botul și arată meniul principal")]
    )
    if ADMIN_CHAT_ID:
        await application.bot.set_my_commands(
            [
                BotCommand("start", "Pornește botul și arată meniul principal"),
                BotCommand("raport", "Evidența XP a tuturor membrilor"),
                BotCommand("backup", "Descarcă o copie a bazei de date"),
                BotCommand("setxp", "Actualizează XP din listă lipită"),
            ],
            scope=BotCommandScopeChat(chat_id=ADMIN_CHAT_ID),
        )


def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).post_init(_post_init).build()

    application.add_handler(CommandHandler("raport", report.report_command))
    application.add_handler(CommandHandler("backup", backup.backup_command))

    setxp_conv = ConversationHandler(
        entry_points=[CommandHandler("setxp", setxp.start)],
        states={
            setxp.WAITING: [
                MessageHandler(setxp.text_filter, setxp.receive_list),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
        },
        fallbacks=[CommandHandler("cancel", setxp.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(setxp_conv)

    submission_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(submission.start_submission, pattern=r"^sub:(tg|dc|both|comp):(std|pu):start$")
        ],
        states={
            submission.NUME: [
                MessageHandler(submission.text_filter, submission.receive_nume),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            submission.PRENUME: [
                MessageHandler(submission.text_filter, submission.receive_prenume),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            submission.EMAIL: [
                MessageHandler(submission.text_filter, submission.receive_email),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            submission.DISCORD_USERNAME: [
                MessageHandler(submission.text_filter, submission.receive_discord_username),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            submission.PROOF: [
                MessageHandler(submission.proof_filter, submission.receive_proof),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", submission.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(submission_conv)

    myfxbook_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(competition.ask_myfxbook_link, pattern=r"^comp:step:4$")],
        states={
            competition.MYFXBOOK_LINK: [
                MessageHandler(competition.text_filter, competition.receive_myfxbook_link),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
        },
        fallbacks=[CommandHandler("cancel", competition.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(myfxbook_conv)

    trade_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(trade.start, pattern=r"^trade:start$")],
        states={
            trade.PHOTO: [
                MessageHandler(trade.photo_filter, trade.receive_photo),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", trade.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(trade_conv)

    feedback_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(feedback.start, pattern=r"^feedback:start$")],
        states={
            feedback.PHOTO: [
                MessageHandler(feedback.photo_filter, feedback.receive_photo),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", feedback.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(feedback_conv)

    checkin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkin.start, pattern=r"^checkin:start$")],
        states={
            checkin.Q1: [
                CallbackQueryHandler(checkin.q1, pattern=r"^ci:q1:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkin.Q2: [
                CallbackQueryHandler(checkin.q2, pattern=r"^ci:q2:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkin.Q3: [
                CallbackQueryHandler(checkin.q3, pattern=r"^ci:q3:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkin.Q4: [
                CallbackQueryHandler(checkin.q4, pattern=r"^ci:q4:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkin.Q5: [
                CallbackQueryHandler(checkin.q5, pattern=r"^ci:q5:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkin.Q5_CUSTOM: [
                MessageHandler(checkin.text_filter, checkin.q5_custom),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            checkin.Q6: [
                CallbackQueryHandler(checkin.q6, pattern=r"^ci:q6:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkin.Q7: [
                CallbackQueryHandler(checkin.q7, pattern=r"^ci:q7:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
        },
        fallbacks=[CommandHandler("cancel", checkin.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(checkin_conv)

    checkout_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkout.start, pattern=r"^checkout:start$")],
        states={
            checkout.Q1: [
                CallbackQueryHandler(checkout.q1, pattern=r"^co:q1:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkout.Q2: [
                CallbackQueryHandler(checkout.q2, pattern=r"^co:q2:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkout.Q3: [
                CallbackQueryHandler(checkout.q3, pattern=r"^co:q3:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
            checkout.Q4_TEXT: [
                MessageHandler(checkout.text_filter, checkout.q4_text),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            checkout.Q5_TEXT: [
                MessageHandler(checkout.text_filter, checkout.q5_text),
                MessageHandler(filters.ALL & ~filters.COMMAND, _hint_needs_text),
            ],
            checkout.Q6: [
                CallbackQueryHandler(checkout.q6, pattern=r"^co:q6:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, _hint_needs_button),
            ],
        },
        fallbacks=[CommandHandler("cancel", checkout.cancel), CommandHandler("start", _restart_from_stuck_conversation)],
        conversation_timeout=600,
        allow_reentry=True,
    )
    application.add_handler(checkout_conv)

    # Registered after every ConversationHandler above so that /start first gets a
    # chance to hit each conversation's own "start" fallback (ending a stuck flow)
    # before falling through here for users with no active conversation.
    application.add_handler(
        CommandHandler("start", menu.start_command, filters=filters.ChatType.PRIVATE)
    )

    application.add_handler(CallbackQueryHandler(menu.route, pattern=r"^menu:"))
    application.add_handler(CallbackQueryHandler(broker_flow.route_broker, pattern=r"^brk:"))
    application.add_handler(CallbackQueryHandler(broker_flow.route_onboarding, pattern=r"^onb:"))
    application.add_handler(CallbackQueryHandler(challenge.route, pattern=r"^chl:"))
    application.add_handler(CallbackQueryHandler(competition.route, pattern=r"^comp:step:"))
    application.add_handler(CallbackQueryHandler(faq.show_answer, pattern=r"^faq:\d+$"))
    application.add_handler(CallbackQueryHandler(confirm.confirm, pattern=r"^confirm:"))
    application.add_handler(CallbackQueryHandler(approval.request, pattern=r"^req:"))
    application.add_handler(CallbackQueryHandler(approval.approve, pattern=r"^approve:"))
    application.add_handler(ChatJoinRequestHandler(join.handle_join_request))

    application.add_handler(MessageHandler(filters.ALL, _daily_bonus), group=1)
    application.add_handler(CallbackQueryHandler(_daily_bonus), group=1)

    application.add_error_handler(error_handler)

    application.job_queue.run_daily(
        _send_daily_reminder, time=datetime.time(20, 0, tzinfo=TIMEZONE), days=WEEKDAYS_MON_FRI
    )
    application.job_queue.run_daily(
        _send_checkin_prompt, time=datetime.time(8, 0, tzinfo=TIMEZONE), days=WEEKDAYS_MON_FRI
    )
    application.job_queue.run_daily(
        _send_checkout_prompt, time=datetime.time(19, 0, tzinfo=TIMEZONE), days=WEEKDAYS_MON_FRI
    )
    application.job_queue.run_daily(
        backup.daily_backup_job, time=datetime.time(3, 0, tzinfo=TIMEZONE)
    )

    return application


def main():
    db.init_db()
    application = build_application()
    logger.info("Profit District Bot pornit.")
    application.run_polling(allowed_updates=["message", "callback_query", "chat_join_request"])


if __name__ == "__main__":
    main()
