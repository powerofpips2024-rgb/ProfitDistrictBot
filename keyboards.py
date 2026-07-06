from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import CONTACT_USERNAME, DISCORD_INVITE_LINK, FP_MARKETS_LINK, PU_PRIME_LINK, TELEGRAM_GROUP_LINK, WEBSITE_URL
from texts import (
    CHECKIN_START_BUTTON,
    CHECKOUT_START_BUTTON,
    COMPETITION_LEADERBOARD_URL,
    EVENTS_URL,
    FAQ_LIST,
)

BACK_TO_MAIN = InlineKeyboardButton("🔙 Meniu principal", callback_data="menu:main")


def main_menu(user=None) -> InlineKeyboardMarkup:
    tg_done = bool(user and user["tg_access"])
    dc_done = bool(user and user["dc_access"])
    mentorship_done = bool(user and user["mentorship_confirmed"])
    challenge_done = bool(user and user["challenge_done"])
    show_profile = tg_done or dc_done

    rows = []
    if show_profile:
        rows.append([InlineKeyboardButton("👤 Profilul meu", callback_data="menu:profile")])
    if mentorship_done:
        rows.append([InlineKeyboardButton("🎮 Nivelul meu", callback_data="menu:level")])
        rows.append([InlineKeyboardButton("🏆 Clasament", callback_data="menu:leaderboard")])
    if show_profile:
        rows.append([InlineKeyboardButton("📸 Feedback zilnic", callback_data="feedback:start")])
        rows.append([InlineKeyboardButton("🌅 Daily Check-In", callback_data="checkin:start")])
        rows.append([InlineKeyboardButton("🌙 Daily Check-Out", callback_data="checkout:start")])
    if not mentorship_done:
        rows.append([InlineKeyboardButton("🚀 Începe de aici", callback_data="menu:start")])
        rows.append([InlineKeyboardButton("📚 30 Days Mentorship", callback_data="menu:mentorship")])
    if not tg_done:
        rows.append([InlineKeyboardButton("📈 Telegram", callback_data="menu:telegram")])
    if not dc_done:
        rows.append([InlineKeyboardButton("🔥 Discord", callback_data="menu:discord")])
    if not (tg_done and dc_done):
        rows.append([InlineKeyboardButton("📈🔥 Telegram + Discord", callback_data="menu:tgdc")])
    if not challenge_done:
        rows.append([InlineKeyboardButton("🏆 Challenge 500 → 5.000", callback_data="menu:challenge")])
    rows += [
        [InlineKeyboardButton("🥇 Competiții", callback_data="menu:competitions")],
        [InlineKeyboardButton("📅 Evenimente", callback_data="menu:events")],
        [InlineKeyboardButton("🎁 Resurse gratuite", callback_data="menu:resources")],
        [InlineKeyboardButton("❓ Întrebări frecvente", callback_data="menu:faq")],
        [InlineKeyboardButton("💬 Contactează echipa", callback_data="menu:contact")],
        [InlineKeyboardButton("🌐 Website", url=WEBSITE_URL)],
    ]
    return InlineKeyboardMarkup(rows)


def start_here_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📚 Mentorat", callback_data="menu:mentorship")],
        [InlineKeyboardButton("📈 Telegram", callback_data="menu:telegram")],
        [InlineKeyboardButton("🔥 Discord", callback_data="menu:discord")],
        [InlineKeyboardButton("📈🔥 Telegram + Discord", callback_data="menu:tgdc")],
        [InlineKeyboardButton("🏆 Challenge 500 → 5.000", callback_data="menu:challenge")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def mentorship_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("➡️ Începe acum", url=WEBSITE_URL)],
        [InlineKeyboardButton("✅ Am accesat mentoratul", callback_data="req:mentorship")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def broker_has_broker_menu(product: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("✅ Da", callback_data=f"brk:{product}:has:yes")],
        [InlineKeyboardButton("❌ Nu", callback_data=f"brk:{product}:has:no")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


EXISTING_BROKER_OPTIONS = [
    ("pu", "1. PU Prime"),
    ("robo", "2. RoboForex"),
    ("multibank", "3. Multibank"),
    ("fp", "4. FP Markets / FP Trading"),
    ("ic", "5. IC Markets"),
    ("vantage", "6. Vantage"),
    ("t212", "7. Trading 212"),
    ("xtb", "8. XTB"),
    ("altul", "9. ALTUL"),
]


def broker_existing_menu(product: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data=f"brk:{product}:exi:{code}")]
        for code, label in EXISTING_BROKER_OPTIONS
    ]
    rows.append([BACK_TO_MAIN])
    return InlineKeyboardMarkup(rows)


def broker_capital_menu(product: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("sub 200$", callback_data=f"brk:{product}:cap:under200")],
        [InlineKeyboardButton("peste 200$", callback_data=f"brk:{product}:cap:over200")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def broker_priority_menu(product: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("costuri mici", callback_data=f"brk:{product}:pri:cost")],
        [InlineKeyboardButton("copy trading", callback_data=f"brk:{product}:pri:copy")],
        [InlineKeyboardButton("bonus depozit", callback_data=f"brk:{product}:pri:bonus")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def broker_recommendation_menu(
    product: str, broker_link: str, show_support: bool = False
) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🔗 Creează cont", url=broker_link)],
        [InlineKeyboardButton("➡️ Continuă", callback_data=f"onb:{product}:step:1")],
    ]
    if show_support:
        rows.append([InlineKeyboardButton("📞 Contactează suport", url=f"https://t.me/{CONTACT_USERNAME}")])
    rows.append([BACK_TO_MAIN])
    return InlineKeyboardMarkup(rows)


def onboarding_step_menu(product: str, step: int, confirm_label: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(confirm_label, callback_data=f"onb:{product}:step:{step}")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def submission_start_menu(product: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📝 Trimite datele", callback_data=f"sub:{product}:std:start")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def pu_prime_continue_menu(product: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("➡️ Am creat cont și am depozitat", callback_data=f"sub:{product}:pu:start")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def challenge_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🔗 Creează cont PU Prime", url=PU_PRIME_LINK)],
        [InlineKeyboardButton("➡️ Continuă", callback_data="chl:step:2")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def challenge_step_menu(next_callback: str, label: str = "➡️ Continuă") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(label, callback_data=next_callback)],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def challenge_success_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("✅ M-am înscris", callback_data="req:challenge")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def faq_list_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(question, callback_data=f"faq:{i}")]
        for i, (question, _) in enumerate(FAQ_LIST)
    ]
    rows.append([BACK_TO_MAIN])
    return InlineKeyboardMarkup(rows)


def faq_answer_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🔙 Înapoi la FAQ", callback_data="menu:faq")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def back_to_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[BACK_TO_MAIN]])


def level_menu(show_trade_button: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if show_trade_button:
        rows.append([InlineKeyboardButton("📸 Trimite dovada primului trade", callback_data="trade:start")])
    rows.append([BACK_TO_MAIN])
    return InlineKeyboardMarkup(rows)


def profile_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📞 Contactează echipa", callback_data="menu:contact")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def competitions_intro_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🚀 Vreau să particip", callback_data="menu:comp_join")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def competition_step2_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🆘 Am nevoie de suport", url=f"https://t.me/{CONTACT_USERNAME}")],
        [InlineKeyboardButton("✅ Gata", callback_data="comp:step:3")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def competition_step3_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("✅ Gata", callback_data="comp:step:4")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def competition_success_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🏆 Vezi clasamentul", url=COMPETITION_LEADERBOARD_URL)],
        [InlineKeyboardButton("✅ M-am înscris", callback_data="req:competition")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def events_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("Vreau detalii", url=EVENTS_URL)],
        [InlineKeyboardButton("✅ M-am înscris", callback_data="req:event")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def access_link_menu(product: str) -> InlineKeyboardMarkup:
    if product == "both":
        rows = [
            [InlineKeyboardButton("📈 Intră în grup Telegram", url=TELEGRAM_GROUP_LINK)],
            [InlineKeyboardButton("🔥 Intră pe Discord", url=DISCORD_INVITE_LINK)],
            [InlineKeyboardButton("✅ Am intrat", callback_data="confirm:tgdc_access")],
            [BACK_TO_MAIN],
        ]
        return InlineKeyboardMarkup(rows)

    link = TELEGRAM_GROUP_LINK if product == "tg" else DISCORD_INVITE_LINK
    label = "📈 Intră în grup" if product == "tg" else "🔥 Intră pe Discord"
    confirm_field = "tg_access" if product == "tg" else "dc_access"
    rows = [
        [InlineKeyboardButton(label, url=link)],
        [InlineKeyboardButton("✅ Am intrat", callback_data=f"confirm:{confirm_field}")],
        [BACK_TO_MAIN],
    ]
    return InlineKeyboardMarkup(rows)


def checkin_prompt_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(CHECKIN_START_BUTTON, callback_data="checkin:start")]])


def checkin_q1_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Da", callback_data="ci:q1:yes"), InlineKeyboardButton("❌ Nu", callback_data="ci:q1:no")],
        ]
    )


def checkin_q2_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌏 Asia", callback_data="ci:q2:asia")],
            [InlineKeyboardButton("🇬🇧 Londra", callback_data="ci:q2:london")],
            [InlineKeyboardButton("🇺🇸 New York", callback_data="ci:q2:ny")],
            [InlineKeyboardButton("❌ Nu tranzacționez astăzi", callback_data="ci:q2:none")],
        ]
    )


def checkin_q3_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("😌 Foarte bine", callback_data="ci:q3:great")],
            [InlineKeyboardButton("🙂 Bine", callback_data="ci:q3:good")],
            [InlineKeyboardButton("😐 Neutru", callback_data="ci:q3:neutral")],
            [InlineKeyboardButton("😕 Stresat", callback_data="ci:q3:stressed")],
            [InlineKeyboardButton("😴 Obosit", callback_data="ci:q3:tired")],
        ]
    )


def checkin_q4_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📚 Să învăț", callback_data="ci:q4:learn")],
            [InlineKeyboardButton("📈 Să caut un setup bun", callback_data="ci:q4:setup")],
            [InlineKeyboardButton("🎯 Să respect planul", callback_data="ci:q4:plan")],
            [InlineKeyboardButton("🚫 Să nu forțez tranzacții", callback_data="ci:q4:noforce")],
        ]
    )


def checkin_q5_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("0.5%", callback_data="ci:q5:0.5%"),
                InlineKeyboardButton("1%", callback_data="ci:q5:1%"),
                InlineKeyboardButton("2%", callback_data="ci:q5:2%"),
            ],
            [InlineKeyboardButton("Altul", callback_data="ci:q5:other")],
        ]
    )


def checkin_q6_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Da", callback_data="ci:q6:yes")],
            [InlineKeyboardButton("🤝 Mă voi strădui", callback_data="ci:q6:try")],
        ]
    )


def checkin_q7_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Da", callback_data="ci:q7:yes"), InlineKeyboardButton("❌ Nu", callback_data="ci:q7:no")],
        ]
    )


def checkout_prompt_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(CHECKOUT_START_BUTTON, callback_data="checkout:start")]])


def checkout_q1_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Da", callback_data="co:q1:yes"), InlineKeyboardButton("❌ Nu", callback_data="co:q1:no")],
        ]
    )


def checkout_q2_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Da", callback_data="co:q2:yes")],
            [InlineKeyboardButton("⚠️ Parțial", callback_data="co:q2:partial")],
            [InlineKeyboardButton("❌ Nu", callback_data="co:q2:no")],
        ]
    )


def checkout_q3_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("😊 Mulțumit", callback_data="co:q3:happy")],
            [InlineKeyboardButton("😐 Neutru", callback_data="co:q3:neutral")],
            [InlineKeyboardButton("😞 Dezamăgit", callback_data="co:q3:disappointed")],
        ]
    )


def checkout_q6_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Da", callback_data="co:q6:yes")],
            [InlineKeyboardButton("🤔 Parțial", callback_data="co:q6:partial")],
            [InlineKeyboardButton("❌ Nu", callback_data="co:q6:no")],
        ]
    )
