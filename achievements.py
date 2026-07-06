from levels import LEVELS

ELITE_XP_THRESHOLD = LEVELS[-1][0]

AUTO_ACHIEVEMENTS = [
    ("mentorship_confirmed", "🏅 Mentorat Finalizat"),
    ("community", "🏅 Community Member"),
    ("challenge_done", "🏅 Challenge Accepted"),
    ("event_confirmed", "🏅 Primul Webinar"),
    ("elite", "🏅 Elite Trader"),
]

MANUAL_ACHIEVEMENTS = [
    ("first_trade_confirmed", "🏅 Primul Trade"),
]


def _is_unlocked(user, key: str) -> bool:
    if key == "community":
        return bool(user["tg_access"] or user["dc_access"])
    if key == "elite":
        return user["xp"] >= ELITE_XP_THRESHOLD
    return bool(user[key])


def achievement_status(user) -> list[tuple[str, bool]]:
    all_achievements = AUTO_ACHIEVEMENTS + MANUAL_ACHIEVEMENTS
    return [(label, _is_unlocked(user, key)) for key, label in all_achievements]
