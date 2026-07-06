async def edit_or_send(query, text, reply_markup=None, parse_mode=None):
    if query.message.photo:
        try:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
