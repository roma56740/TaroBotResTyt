from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

# ---------- Основные клавиатуры ----------

def get_user_keyboard():
    keyboard = [
        [KeyboardButton(text="💬 Отзывы"), KeyboardButton(text="🎁 Подарок")],
        [KeyboardButton(text="🛠 Услуги"), KeyboardButton(text="📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_admin_keyboard():
    keyboard = [
        [KeyboardButton(text="📊 Анализ"), KeyboardButton(text="⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_settings_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📝 Приветствие", callback_data="greeting_menu")],
        [InlineKeyboardButton(text="💬 Отзывы", callback_data="edit_reviews")],
        [InlineKeyboardButton(text="🛠 Услуги", callback_data="services_menu")],
        [InlineKeyboardButton(text="🎁 Подарки", callback_data="gifts_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------- Приветствие (подменю) ----------
def get_greeting_menu():
    buttons = [
        [InlineKeyboardButton(text="✅ Посмотреть", callback_data="view_greeting")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_greeting")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------- Отзывы (админ) ----------
def get_reviews_menu():
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить отзыв", callback_data="reviews_add")],
        [InlineKeyboardButton(text="🗑 Удалить отзыв", callback_data="reviews_delete_page:0")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_reviews_delete_keyboard(page: int, page_size: int, total: int, items):
    rows = []
    for r_id, author, text, date in items:
        label = f"🗑 {author} • {date}"
        rows.append([InlineKeyboardButton(
            text=label[:64],
            callback_data=f"reviews_delete_id:{r_id}:{page}"
        )])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"reviews_delete_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"reviews_delete_page:{page+1}"))
    if nav_row:
        rows.append(nav_row)

    rows.append([InlineKeyboardButton(text="↩️ В меню отзывов", callback_data="greeting_reviews_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- Услуги (админ) ----------
def get_services_menu():
    buttons = [
        [InlineKeyboardButton(text="👀 Посмотреть", callback_data="services_view_page:0")],
        [InlineKeyboardButton(text="➕ Добавить", callback_data="services_add")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="services_delete_page:0")],
        [InlineKeyboardButton(text="↩️ Назад к настройкам", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_services_view_keyboard(page: int, page_size: int, total: int):
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"services_view_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"services_view_page:{page+1}"))

    rows = []
    if nav_row:
        rows.append(nav_row)
    rows.append([InlineKeyboardButton(text="↩️ В меню услуг", callback_data="services_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_services_delete_keyboard(page: int, page_size: int, total: int, items):
    rows = []
    for s_id, name, description, file_path in items:
        label = f"🗑 {name}"
        rows.append([InlineKeyboardButton(
            text=label[:64],
            callback_data=f"services_delete_id:{s_id}:{page}"
        )])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"services_delete_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"services_delete_page:{page+1}"))
    if nav_row:
        rows.append(nav_row)

    rows.append([InlineKeyboardButton(text="↩️ В меню услуг", callback_data="services_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- Подарки (админ) ----------
def get_gifts_menu():
    buttons = [
        [InlineKeyboardButton(text="👀 Посмотреть", callback_data="gifts_view_page:0")],
        [InlineKeyboardButton(text="➕ Добавить", callback_data="gifts_add")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="gifts_delete_page:0")],
        [InlineKeyboardButton(text="↩️ Назад к настройкам", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_gifts_view_keyboard(page: int, page_size: int, total: int):
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"gifts_view_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"gifts_view_page:{page+1}"))

    rows = []
    if nav_row:
        rows.append(nav_row)
    rows.append([InlineKeyboardButton(text="↩️ В меню подарков", callback_data="gifts_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_gifts_delete_keyboard(page: int, page_size: int, total: int, items):
    rows = []
    for g_id, name, description, file_path in items:
        label = f"🗑 {name}"
        rows.append([InlineKeyboardButton(
            text=label[:64],
            callback_data=f"gifts_delete_id:{g_id}:{page}"
        )])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"gifts_delete_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"gifts_delete_page:{page+1}"))
    if nav_row:
        rows.append(nav_row)

    rows.append([InlineKeyboardButton(text="↩️ В меню подарков", callback_data="gifts_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------- Пользовательские списки/детали ----------

def get_user_reviews_keyboard(page: int, page_size: int, total: int, items):
    rows = []
    for r_id, author, text, date in items:
        label = f"💬 {author} • {date}"
        rows.append([InlineKeyboardButton(
            text=label[:64],
            callback_data=f"u_review_id:{r_id}:{page}"
        )])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"u_reviews_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"u_reviews_page:{page+1}"))
    if nav_row:
        rows.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_user_services_keyboard(page: int, page_size: int, total: int, items):
    rows = []
    for s_id, name, description, file_path in items:
        rows.append([InlineKeyboardButton(
            text=f"🛠 {name}"[:64],
            callback_data=f"u_service_id:{s_id}:{page}"
        )])
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"u_services_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"u_services_page:{page+1}"))
    if nav_row:
        rows.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_user_gifts_keyboard(page: int, page_size: int, total: int, items):
    rows = []
    for g_id, name, description, file_path in items:
        rows.append([InlineKeyboardButton(
            text=f"🎁 {name}"[:64],
            callback_data=f"u_gift_id:{g_id}:{page}"
        )])
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"u_gifts_page:{page-1}"))
    if (page + 1) * page_size < total:
        nav_row.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"u_gifts_page:{page+1}"))
    if nav_row:
        rows.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Контакты — одна кнопка «Перейти» с URL
def get_contacts_keyboard(url: str, text: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"➡️ {text}", url=url)]
    ])


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_skip_file_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить файл", callback_data="skip_file")]
        ]
    )
    return keyboard
