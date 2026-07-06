async def edit_or_send(query, text, reply_markup=None, parse_mode=None):
    if query.message.photo:
        try:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        try:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            # A malformed URL button, an over-length message, a stale/expired
            # message, etc. would otherwise raise silently here: the user's
            # loading spinner stops (query.answer() already happened) but the
            # screen never updates, looking exactly like a dead button. Always
            # fall back to sending a fresh message so something visible happens.
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
