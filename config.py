import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "").strip()

WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://profitdistrictromania.com")
TELEGRAM_GROUP_LINK = os.environ.get("TELEGRAM_GROUP_LINK", "https://t.me/+PLACEHOLDER")
DISCORD_INVITE_LINK = os.environ.get("DISCORD_INVITE_LINK", "https://discord.gg/PLACEHOLDER")
CONTACT_USERNAME = os.environ.get("CONTACT_USERNAME", "hanetrades")

FP_MARKETS_LINK = os.environ.get("FP_MARKETS_LINK", "https://PLACEHOLDER-fp-markets-affiliate-link")
PU_PRIME_LINK = os.environ.get("PU_PRIME_LINK", "https://PLACEHOLDER-pu-prime-affiliate-link")
