import sqlite3
from datetime import date
from pathlib import Path

import config

DB_PATH = Path(config.DB_PATH) if config.DB_PATH else Path(__file__).parent / "data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            has_broker TEXT,
            existing_broker TEXT,
            capital TEXT,
            priority TEXT,
            broker_recommended TEXT,
            product TEXT,
            identity_verified INTEGER DEFAULT 0,
            address_verified INTEGER DEFAULT 0,
            deposit_done INTEGER DEFAULT 0,
            nume TEXT,
            prenume TEXT,
            email TEXT,
            proof_file_id TEXT,
            discord_username TEXT,
            access_granted INTEGER DEFAULT 0,
            tg_access INTEGER DEFAULT 0,
            dc_access INTEGER DEFAULT 0,
            challenge_done INTEGER DEFAULT 0,
            mentorship_confirmed INTEGER DEFAULT 0,
            competition_done INTEGER DEFAULT 0,
            event_confirmed INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            mentorship_started INTEGER DEFAULT 0,
            last_xp_day TEXT,
            streak INTEGER DEFAULT 0,
            last_feedback_day TEXT,
            first_trade_confirmed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_checkin (
            telegram_id INTEGER,
            day TEXT,
            analyzed_market TEXT,
            session TEXT,
            mood TEXT,
            goal TEXT,
            risk TEXT,
            respect_plan TEXT,
            checked_news TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (telegram_id, day)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_checkout (
            telegram_id INTEGER,
            day TEXT,
            traded TEXT,
            respected_plan TEXT,
            day_feeling TEXT,
            learned_text TEXT,
            improve_text TEXT,
            identity_answer TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (telegram_id, day)
        )
        """
    )
    conn.commit()
    for column_def in (
        "existing_broker TEXT",
        "tg_access INTEGER DEFAULT 0",
        "dc_access INTEGER DEFAULT 0",
        "challenge_done INTEGER DEFAULT 0",
        "mentorship_confirmed INTEGER DEFAULT 0",
        "competition_done INTEGER DEFAULT 0",
        "event_confirmed INTEGER DEFAULT 0",
        "xp INTEGER DEFAULT 0",
        "mentorship_started INTEGER DEFAULT 0",
        "last_xp_day TEXT",
        "streak INTEGER DEFAULT 0",
        "last_feedback_day TEXT",
        "first_trade_confirmed INTEGER DEFAULT 0",
    ):
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {column_def}")
            conn.commit()
        except sqlite3.OperationalError:
            pass
    conn.close()


def upsert_user(telegram_id: int, username: str | None, first_name: str | None):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO users (telegram_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            updated_at = CURRENT_TIMESTAMP
        """,
        (telegram_id, username, first_name),
    )
    conn.commit()
    conn.close()


def update_user(telegram_id: int, **fields):
    if not fields:
        return
    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [telegram_id]
    conn = get_connection()
    conn.execute(
        f"UPDATE users SET {columns}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
        values,
    )
    conn.commit()
    conn.close()


def add_xp(telegram_id: int, amount: int):
    if not amount:
        return
    conn = get_connection()
    conn.execute(
        "UPDATE users SET xp = xp + ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
        (amount, telegram_id),
    )
    conn.commit()
    conn.close()


def award_daily_bonus(telegram_id: int) -> bool:
    today = date.today()
    today_iso = today.isoformat()
    conn = get_connection()
    row = conn.execute(
        "SELECT last_xp_day, streak FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    if row is None or row["last_xp_day"] == today_iso:
        conn.close()
        return False

    consecutive = False
    if row["last_xp_day"]:
        consecutive = (today - date.fromisoformat(row["last_xp_day"])).days == 1
    new_streak = (row["streak"] or 0) + 1 if consecutive else 1

    conn.execute(
        "UPDATE users SET xp = xp + 10, last_xp_day = ?, streak = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE telegram_id = ?",
        (today_iso, new_streak, telegram_id),
    )
    conn.commit()
    conn.close()
    return True


def record_daily_feedback(telegram_id: int) -> bool:
    today = date.today().isoformat()
    conn = get_connection()
    row = conn.execute(
        "SELECT last_feedback_day FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    if row is None or row["last_feedback_day"] == today:
        conn.close()
        return False
    conn.execute(
        "UPDATE users SET xp = xp + 10, last_feedback_day = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE telegram_id = ?",
        (today, telegram_id),
    )
    conn.commit()
    conn.close()
    return True


def find_user_by_username(username: str) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)
    ).fetchone()
    conn.close()
    return row


def find_user_by_first_name(name: str) -> sqlite3.Row | None:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM users WHERE first_name = ? COLLATE NOCASE", (name,)
    ).fetchall()
    conn.close()
    return rows[0] if len(rows) == 1 else None


def get_leaderboard(limit: int = 10) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT telegram_id, first_name, xp FROM users ORDER BY xp DESC, telegram_id ASC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return rows


def get_xp_rank(telegram_id: int) -> int | None:
    conn = get_connection()
    row = conn.execute("SELECT xp FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
    if row is None:
        conn.close()
        return None
    rank_row = conn.execute(
        "SELECT COUNT(*) AS higher FROM users WHERE xp > ?", (row["xp"],)
    ).fetchone()
    conn.close()
    return rank_row["higher"] + 1


def all_telegram_ids() -> list[int]:
    conn = get_connection()
    rows = conn.execute("SELECT telegram_id FROM users").fetchall()
    conn.close()
    return [row["telegram_id"] for row in rows]


def checkin_exists_today(telegram_id: int) -> bool:
    today = date.today().isoformat()
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM daily_checkin WHERE telegram_id = ? AND day = ?", (telegram_id, today)
    ).fetchone()
    conn.close()
    return row is not None


def save_checkin(telegram_id: int, **fields):
    day = date.today().isoformat()
    columns = ["telegram_id", "day"] + list(fields.keys())
    placeholders = ", ".join("?" for _ in columns)
    values = [telegram_id, day] + list(fields.values())
    conn = get_connection()
    conn.execute(
        f"INSERT OR REPLACE INTO daily_checkin ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
    conn.close()


def save_checkout(telegram_id: int, **fields):
    day = date.today().isoformat()
    columns = ["telegram_id", "day"] + list(fields.keys())
    placeholders = ", ".join("?" for _ in columns)
    values = [telegram_id, day] + list(fields.values())
    conn = get_connection()
    conn.execute(
        f"INSERT OR REPLACE INTO daily_checkout ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
    conn.close()


def get_user(telegram_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    conn.close()
    return row
