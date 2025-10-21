import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Поддержка нескольких админов
ADMIN_IDS = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
]

# Старый формат для обратной совместимости
if not ADMIN_IDS and os.getenv("ADMIN_ID"):
    ADMIN_IDS = [int(os.getenv("ADMIN_ID"))]

# URL для кнопки «Контакты»
CONTACT_URL = os.getenv("CONTACT_URL", "https://t.me/your_contact_here")
CONTACT_BUTTON_TEXT = os.getenv("CONTACT_BUTTON_TEXT", "Перейти")
