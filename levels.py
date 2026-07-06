LEVELS = [
    (0, "🌱 Rookie", ["Acces 30 Days Mentorship"]),
    (100, "📈 Explorer", ["Acces Telegram + Discord + Competiții"]),
    (300, "🎯 Trader", ["Acces prioritar Challenge"]),
    (700, "🔥 Consistent", ["Reducere la evenimente", "Acces webinar exclusiv (unul pe lună)"]),
    (
        1500,
        "💎 Elite",
        [
            "Sesiuni Q&A",
            "Badge special Discord",
            "Acces prioritar suport",
            "Acces sesiuni 1-1",
            "Grup special",
        ],
    ),
]


def level_for_xp(xp: int) -> tuple[int, str, list[str]]:
    current = LEVELS[0]
    for threshold, name, benefits in LEVELS:
        if xp >= threshold:
            current = (threshold, name, benefits)
        else:
            break
    return current


def next_level_for_xp(xp: int) -> tuple[int, str, list[str]] | None:
    for threshold, name, benefits in LEVELS:
        if xp < threshold:
            return (threshold, name, benefits)
    return None


def unlocked_benefits(xp: int) -> list[str]:
    benefits = []
    for threshold, _, level_benefits in LEVELS:
        if xp >= threshold:
            benefits.extend(level_benefits)
    return benefits


def progress_bar(xp: int, blocks: int = 10) -> str:
    next_level = next_level_for_xp(xp)
    if next_level is None:
        return "█" * blocks

    current_threshold = level_for_xp(xp)[0]
    next_threshold = next_level[0]
    span = next_threshold - current_threshold
    done = xp - current_threshold
    filled = min(blocks, round((done / span) * blocks)) if span else blocks
    return "█" * filled + "░" * (blocks - filled)
