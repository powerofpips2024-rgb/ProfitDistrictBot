import logging

logger = logging.getLogger(__name__)


async def edit_or_send(query, text, reply_markup=None, parse_mode=None):
    if query.message.photo:
        try:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            return
        except Exception:
            pass
    else:
        try:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            return
        except Exception:
            pass

    # Editing failed (malformed URL button, stale/expired message, message
    # too long, etc.) -- the user's loading spinner already stopped
    # (query.answer() happens before this is called), so without a fallback
    # the screen just never updates, looking exactly like a dead button.
    try:
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        return
    except Exception:
        pass

    # If the SAME thing that broke the edit (e.g. an invalid button URL) also
    # breaks this fresh message, sending again with the identical markup would
    # fail identically. Drop the keyboard so the user at least sees the text
    # instead of total silence.
    try:
        await query.message.reply_text(text, parse_mode=parse_mode)
    except Exception:
        logger.exception("edit_or_send: nu am putut afișa conținutul în niciun fel")
