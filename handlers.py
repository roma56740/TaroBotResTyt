import os
from uuid import uuid4

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from config import ADMIN_IDS

from config import ADMIN_ID, CONTACT_URL, CONTACT_BUTTON_TEXT
from keyboards import (
    get_user_keyboard, get_admin_keyboard,
    get_settings_keyboard, get_greeting_menu,
    get_reviews_menu, get_reviews_delete_keyboard,
    get_services_menu, get_services_view_keyboard, get_services_delete_keyboard, get_skip_file_keyboard,
    get_gifts_menu, get_gifts_view_keyboard, get_gifts_delete_keyboard,
    get_user_reviews_keyboard, get_user_services_keyboard, get_user_gifts_keyboard,
    get_contacts_keyboard
)
from database import (
    save_greeting, get_greeting,
    add_review, list_reviews, count_reviews, delete_review, get_review_by_id,
    add_service, list_services, count_services, delete_service, get_service_by_id,
    add_gift, list_gifts, count_gifts, delete_gift, get_gift_by_id
)

router = Router()

GREETING_FOLDER = "media/greetings"
SERVICES_FOLDER = "media/services"
GIFTS_FOLDER = "media/gifts"
PAGE_SIZE = 5

IMG_FOLDER = "media/img"
BTN_IMG = {
    "reviews": "Otz.png",
    "gifts":   "Sur.png",
    "services":"Tool.png",
    "contacts":"Call.png",
}

# ============ helpers ============

def _img_path(key: str) -> str | None:
    """Вернёт полный путь к картинке для раздела, если файл существует."""
    name = BTN_IMG.get(key)
    if not name:
        return None
    path = os.path.join(IMG_FOLDER, name)
    return path if os.path.exists(path) else None


async def _remember(state: FSMContext, msg):
    data = await state.get_data()
    cleanup = data.get("cleanup", [])
    cleanup.append((msg.chat.id, msg.message_id))
    await state.update_data(cleanup=cleanup)

async def _purge(state: FSMContext, bot: Bot):
    data = await state.get_data()
    for chat_id, mid in data.get("cleanup", []):
        try:
            await bot.delete_message(chat_id, mid)
        except Exception:
            pass
    await state.update_data(cleanup=[])

def _is_image(filepath: str) -> bool:
    ext = os.path.splitext(filepath.lower())[1]
    return ext in {".jpg", ".jpeg", ".png", ".webp"}


# ============ FSM ============

class GreetingFSM(StatesGroup):
    waiting_for_photo = State()
    waiting_for_text = State()

class ReviewFSM(StatesGroup):
    waiting_author = State()
    waiting_text = State()
    waiting_date = State()

class ServiceFSM(StatesGroup):
    waiting_name = State()
    waiting_desc = State()
    waiting_file = State()

class GiftFSM(StatesGroup):
    waiting_name = State()
    waiting_desc = State()
    waiting_file = State()


# =====================================================================
#                              /start
# =====================================================================

@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        text = (
            "👋 <b>Привет, админ!</b>\n\n"
            "Добро пожаловать в панель управления.\n\n"
            "• <b>📊 Анализ</b> — короткая сводка по контенту.\n"
            "• <b>⚙️ Настройки</b> — редактирование приветствия, отзывов, услуг и подарков.\n\n"
            "Готовы творить магию? ✨"
        )
        await message.answer(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
        return

    greeting = get_greeting()
    if greeting and greeting[0] and os.path.exists(greeting[0]):
        await message.answer_photo(
            FSInputFile(greeting[0]),
            caption=greeting[1],
            reply_markup=get_user_keyboard()
        )
    else:
        text = (
            "✨ <b>Добро пожаловать!</b>\n\n"
            "Этот бот — ваш гид по нашему миру:\n\n"
            "• <b>💬 Отзывы</b> — почитайте, что говорят о нас реальные люди.\n"
            "• <b>🎁 Подарок</b> — специальные предложения и приятные сюрпризы.\n"
            "• <b>🛠 Услуги</b> — полный список того, чем мы можем помочь.\n"
            "• <b>📞 Контакты</b> — быстро свяжитесь с нами в один клик.\n\n"
            "Выбирайте раздел ниже и поехали! 🚀"
        )
        await message.answer(text, reply_markup=get_user_keyboard(), parse_mode="HTML")


# =====================================================================
#                               АДМИН
# =====================================================================

# ---------- Анализ ----------
@router.message(F.text == "📊 Анализ")
async def admin_analytics(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    total_reviews = count_reviews()
    total_services = count_services()
    total_gifts = count_gifts()
    text = (
        "📈 <b>Аналитика проекта</b>\n\n"
        f"💬 Отзывов: <b>{total_reviews}</b>\n"
        f"🛠 Услуг: <b>{total_services}</b>\n"
        f"🎁 Подарков: <b>{total_gifts}</b>\n\n"
        "Поддерживайте актуальность контента — это прямой путь к доверию и продажам.🔥"
    )
    await message.answer(text, parse_mode="HTML")


# ---------- Настройки ----------
@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message):
    if message.from_user.id == ADMIN_ID:
        text = (
            "🛠 <b>Настройки</b>\n\n"
            "Что будем менять?\n"
            "• Приветствие — первое впечатление решает всё.\n"
            "• Отзывы — социальное доказательство.\n"
            "• Услуги — ваша экспертиза.\n"
            "• Подарки — «вау»-эффект и любовь клиентов. 💝"
        )
        await message.answer(text, reply_markup=get_settings_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    text = (
        "🛠 <b>Настройки</b>\n\n"
        "Выберите раздел для редактирования."
    )
    await callback.message.edit_text(text, reply_markup=get_settings_keyboard(), parse_mode="HTML")


# ---------- Приветствие ----------
@router.callback_query(F.data == "greeting_menu")
async def greeting_menu(callback: CallbackQuery):
    text = (
        "🔧 <b>Редактирование приветствия</b>\n\n"
        "Сделайте вход ярким: картинка + короткое, цепляющее сообщение."
    )
    await callback.message.edit_text(text, reply_markup=get_greeting_menu(), parse_mode="HTML")

@router.callback_query(F.data == "view_greeting")
async def view_greeting(callback: CallbackQuery):
    greeting = get_greeting()
    if greeting and greeting[0] and os.path.exists(greeting[0]):
        await callback.message.answer_photo(FSInputFile(greeting[0]), caption=greeting[1])
    else:
        await callback.message.answer("❗ Приветствие ещё не настроено. Загрузите фото и текст.")

@router.callback_query(F.data == "edit_greeting")
async def edit_greeting(callback: CallbackQuery, state: FSMContext):
    os.makedirs(GREETING_FOLDER, exist_ok=True)
    prompt = await callback.message.answer(
        "📷 Отправьте <b>новое фото</b> для приветствия.\n\n"
        "Совет: светлая картинка без мелкого текста работает лучше. ✨",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(GreetingFSM.waiting_for_photo)

@router.message(GreetingFSM.waiting_for_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext, bot: Bot):
    tg_file = await bot.get_file(message.photo[-1].file_id)
    filename = f"{uuid4()}.jpg"
    path = os.path.join(GREETING_FOLDER, filename)
    await bot.download_file(tg_file.file_path, path)

    await state.update_data(photo_path=path)
    await _remember(state, message)

    prompt = await message.answer(
        "✏️ Теперь отправьте <b>текст</b> приветствия.\n\n"
        "Лучше коротко и по делу: ценность + призыв к действию. 💡",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(GreetingFSM.waiting_for_text)

@router.message(GreetingFSM.waiting_for_text)
async def receive_text(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await _remember(state, message)
    save_greeting(data["photo_path"], message.text)

    await _purge(state, bot)
    await state.clear()
    await message.answer("✅ Готово! Приветствие обновлено. Новый пользователь скажет: «Вау!» 😍")


# ---------- Отзывы (админ) ----------
@router.callback_query(F.data == "edit_reviews")
async def reviews_root(callback: CallbackQuery):
    text = (
        "🗂 <b>Управление отзывами</b>\n\n"
        "Добавляйте сильные истории клиентов и держите их актуальными.\n"
        "Пара кликов — и доверие растёт. 📈"
    )
    await callback.message.edit_text(text, reply_markup=get_reviews_menu(), parse_mode="HTML")

@router.callback_query(F.data == "greeting_reviews_back")
async def reviews_back(callback: CallbackQuery):
    await reviews_root(callback)  # тот же текст

@router.callback_query(F.data == "reviews_add")
async def reviews_add_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    prompt = await callback.message.answer(
        "🧑 Введите <b>ФИО</b> или <b>@username</b> автора отзыва:",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(ReviewFSM.waiting_author)

@router.message(ReviewFSM.waiting_author, F.text.len() > 0)
async def reviews_add_author(message: Message, state: FSMContext):
    await state.update_data(author=message.text.strip())
    await _remember(state, message)
    prompt = await message.answer("💬 Введите <b>текст</b> отзыва:", parse_mode="HTML")
    await _remember(state, prompt)
    await state.set_state(ReviewFSM.waiting_text)

@router.message(ReviewFSM.waiting_text, F.text.len() > 0)
async def reviews_add_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text.strip())
    await _remember(state, message)
    prompt = await message.answer("📅 Введите <b>дату</b> (например, 07.08.2025):", parse_mode="HTML")
    await _remember(state, prompt)
    await state.set_state(ReviewFSM.waiting_date)

@router.message(ReviewFSM.waiting_date, F.text.len() > 0)
async def reviews_add_date(message: Message, state: FSMContext, bot: Bot):
    d = await state.get_data()
    await _remember(state, message)
    add_review(d["author"], d["text"], message.text.strip())
    await _purge(state, bot)
    await state.clear()
    await message.answer("✅ Отзыв добавлен! Спасибо, это усиливает наш бренд. 💪")

@router.callback_query(F.data.startswith("reviews_delete_page:"))
async def reviews_delete_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    total = count_reviews()
    items = list_reviews(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    if not items:
        await callback.message.edit_text("Пока отзывов нет. Добавьте первый — и начнётся магия! ✨", reply_markup=get_reviews_menu())
        return
    text = f"🗑 <b>Удаление отзывов</b>\nСтраница: <b>{page+1}</b> • Всего: <b>{total}</b>\n\nВыберите отзыв:"
    await callback.message.edit_text(text, reply_markup=get_reviews_delete_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")

@router.callback_query(F.data.startswith("reviews_delete_id:"))
async def reviews_delete_id(callback: CallbackQuery):
    _, rid, page = callback.data.split(":")
    rid, page = int(rid), int(page)
    delete_review(rid)
    await callback.answer("Удалено ✅", show_alert=False)

    total = count_reviews()
    if total == 0:
        await callback.message.edit_text("Все отзывы удалены. Чисто как в океане после шторма. 🌊", reply_markup=get_reviews_menu())
        return
    page = min(page, max((total - 1) // PAGE_SIZE, 0))
    items = list_reviews(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    text = f"🗑 <b>Удаление отзывов</b>\nСтраница: <b>{page+1}</b> • Всего: <b>{total}</b>\n\nВыберите отзыв:"
    await callback.message.edit_text(text, reply_markup=get_reviews_delete_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")


# ---------- Услуги (админ) ----------
@router.callback_query(F.data == "services_menu")
async def services_menu(callback: CallbackQuery):
    text = (
        "🛠 <b>Управление услугами</b>\n\n"
        "Опишите ценность, приложите файлы — и клиенту станет понятнее, зачем вы ему. 💼"
    )
    await callback.message.edit_text(text, reply_markup=get_services_menu(), parse_mode="HTML")

@router.callback_query(F.data.startswith("services_view_page:"))
async def services_view_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
    except Exception:
        page = 0

    total = count_services()

    # Когда услуг нет — показываем меню, но безопасно
    if total == 0:
        text = "Пока услуг нет. Добавьте первую — и начнём продавать! 🚀"
        kb = get_services_menu()
        try:
            if callback.message.text:
                if callback.message.text == text:
                    # Такой же текст — обновим только разметку
                    await callback.message.edit_reply_markup(reply_markup=kb)
                else:
                    await callback.message.edit_text(text, reply_markup=kb)
            else:
                await callback.message.answer(text, reply_markup=kb)
        except TelegramBadRequest:
            # На всякий случай — просто шлём новое сообщение
            await callback.message.answer(text, reply_markup=kb)
        return

    # Есть услуги — рисуем страницу
    items = list_services(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    blocks = []
    for _id, name, desc, file_path in items:
        line = f"• <b>{name}</b>\n{desc[:300]}"
        if file_path:
            line += "\n📎 есть вложение"
        blocks.append(line)

    text = f"👀 <b>Список услуг</b> — страница <b>{page+1}</b>\n\n" + "\n\n".join(blocks)
    kb = get_services_view_keyboard(page, PAGE_SIZE, total)

    try:
        if callback.message.text:
            if callback.message.text == text:
                await callback.message.edit_reply_markup(reply_markup=kb)
            else:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        else:
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "services_add")
async def services_add_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    prompt = await callback.message.answer(
        "📝 Введите <b>название услуги</b>.\n\n"
        "Секрет сильного названия: конкретика + выгода. 😉",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(ServiceFSM.waiting_name)

@router.message(ServiceFSM.waiting_name, F.text.len() > 0)
async def services_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await _remember(state, message)
    prompt = await message.answer(
        "✍️ Опишите <b>суть услуги</b>: что делаем, какой результат и в чём ценность.",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(ServiceFSM.waiting_desc)

@router.message(ServiceFSM.waiting_desc, F.text.len() > 0)
async def services_add_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await _remember(state, message)
    os.makedirs(SERVICES_FOLDER, exist_ok=True)
    prompt = await message.answer(
        "📎 Прикрепите <b>файл</b> (фото/документ) или нажмите «Пропустить».\n\n"
        "Визуал повышает конверсию! 🧲",
        parse_mode="HTML",
        reply_markup=get_skip_file_keyboard()
    )
    await _remember(state, prompt)
    await state.set_state(ServiceFSM.waiting_file)

# принимаем И старый, и новый коллбэк: services_skip_file / skip_file
@router.callback_query((F.data == "services_skip_file") | (F.data == "skip_file"))
async def services_or_gifts_skip_file(callback: CallbackQuery, state: FSMContext, bot: Bot):
    state_name = (await state.get_state()) or ""
    data = await state.get_data()
    if state_name.startswith("ServiceFSM"):
        add_service(data["name"], data["description"], None)
        msg = "✅ Услуга добавлена (без файла). Чётко и по делу!"
    else:
        # GiftFSM
        add_gift(data["name"], data["description"], None)
        msg = "✅ Подарок добавлен (без файла). Пусть будет больше радости!"
    await _purge(state, bot)
    await state.clear()
    await callback.message.answer(msg)

@router.message(ServiceFSM.waiting_file, F.photo | F.document)
async def services_add_file(message: Message, state: FSMContext, bot: Bot):
    os.makedirs(SERVICES_FOLDER, exist_ok=True)
    file_path = None
    if message.photo:
        tg_file = await bot.get_file(message.photo[-1].file_id)
        file_path = os.path.join(SERVICES_FOLDER, f"{uuid4()}.jpg")
        await bot.download_file(tg_file.file_path, file_path)
    elif message.document:
        doc = message.document
        tg_file = await bot.get_file(doc.file_id)
        ext = os.path.splitext(doc.file_name or "")[1] or ".bin"
        file_path = os.path.join(SERVICES_FOLDER, f"{uuid4()}{ext if len(ext) <= 10 else '.bin'}")
        await bot.download_file(tg_file.file_path, file_path)

    await _remember(state, message)
    d = await state.get_data()
    add_service(d["name"], d["description"], file_path)

    await _purge(state, bot)
    await state.clear()
    await message.answer("✅ Услуга добавлена! Супер! 🔥")

@router.callback_query(F.data.startswith("services_delete_page:"))
async def services_delete_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    total = count_services()
    if total == 0:
        await callback.message.edit_text("Пока услуг нет. Самое время добавить первую. ✨", reply_markup=get_services_menu())
        return
    items = list_services(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    text = f"🗑 <b>Удаление услуг</b>\nСтраница: <b>{page+1}</b> • Всего: <b>{total}</b>\n\nВыберите услугу:"
    await callback.message.edit_text(text, reply_markup=get_services_delete_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")

@router.callback_query(F.data.startswith("services_delete_id:"))
async def services_delete_id(callback: CallbackQuery):
    _, sid, page = callback.data.split(":")
    sid, page = int(sid), int(page)
    delete_service(sid)
    await callback.answer("Удалено ✅", show_alert=False)

    total = count_services()
    if total == 0:
        await callback.message.edit_text("Все услуги удалены. Возьмём курс на обновление! 🧭", reply_markup=get_services_menu())
        return
    page = min(page, max((total - 1) // PAGE_SIZE, 0))
    items = list_services(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    text = f"🗑 <b>Удаление услуг</b>\nСтраница: <b>{page+1}</b> • Всего: <b>{total}</b>\n\nВыберите услугу:"
    await callback.message.edit_text(text, reply_markup=get_services_delete_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")


# ---------- Подарки (админ) ----------
@router.callback_query(F.data == "gifts_menu")
async def gifts_menu(callback: CallbackQuery):
    text = (
        "🎁 <b>Управление подарками</b>\n\n"
        "Здесь рождаются спецпредложения, акции и магия «приятно удивить». ✨"
    )
    await callback.message.edit_text(text, reply_markup=get_gifts_menu(), parse_mode="HTML")

@router.callback_query(F.data.startswith("gifts_view_page:"))
async def gifts_view_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    total = count_gifts()
    if total == 0:
        await callback.message.edit_text("Пока подарков нет. Добавьте — и заискрится! ✨", reply_markup=get_gifts_menu())
        return
    items = list_gifts(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    blocks = []
    for _id, name, desc, file_path in items:
        line = f"• <b>{name}</b>\n{desc[:300]}"
        if file_path:
            line += "\n📎 есть вложение"
        blocks.append(line)
    text = f"👀 <b>Список подарков</b> — страница <b>{page+1}</b>\n\n" + "\n\n".join(blocks)
    await callback.message.edit_text(text, reply_markup=get_gifts_view_keyboard(page, PAGE_SIZE, total), parse_mode="HTML")

@router.callback_query(F.data == "gifts_add")
async def gifts_add_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    prompt = await callback.message.answer(
        "📝 Введите <b>название подарка</b>.\n\n"
        "Хорошее название вызывает эмоцию и желание нажать. 💞",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(GiftFSM.waiting_name)

@router.message(GiftFSM.waiting_name, F.text.len() > 0)
async def gifts_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await _remember(state, message)
    prompt = await message.answer(
        "✍️ Напишите <b>описание подарка</b> — коротко, вкусно, с выгодой для клиента.",
        parse_mode="HTML"
    )
    await _remember(state, prompt)
    await state.set_state(GiftFSM.waiting_desc)

@router.message(GiftFSM.waiting_desc, F.text.len() > 0)
async def gifts_add_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await _remember(state, message)
    os.makedirs(GIFTS_FOLDER, exist_ok=True)
    prompt = await message.answer(
        "📎 Прикрепите <b>файл</b> (фото/документ) или нажмите «Пропустить».\n"
        "Красивый визуал — полдела! 🔥",
        parse_mode="HTML",
        reply_markup=get_skip_file_keyboard()
    )
    await _remember(state, prompt)
    await state.set_state(GiftFSM.waiting_file)

@router.message(GiftFSM.waiting_file, F.photo | F.document)
async def gifts_add_file(message: Message, state: FSMContext, bot: Bot):
    os.makedirs(GIFTS_FOLDER, exist_ok=True)
    file_path = None
    if message.photo:
        tg_file = await bot.get_file(message.photo[-1].file_id)
        file_path = os.path.join(GIFTS_FOLDER, f"{uuid4()}.jpg")
        await bot.download_file(tg_file.file_path, file_path)
    elif message.document:
        doc = message.document
        tg_file = await bot.get_file(doc.file_id)
        ext = os.path.splitext(doc.file_name or "")[1] or ".bin"
        file_path = os.path.join(GIFTS_FOLDER, f"{uuid4()}{ext if len(ext) <= 10 else '.bin'}")
        await bot.download_file(tg_file.file_path, file_path)

    await _remember(state, message)
    d = await state.get_data()
    add_gift(d["name"], d["description"], file_path)

    await _purge(state, bot)
    await state.clear()
    await message.answer("✅ Подарок добавлен! Пусть радует людей. 🎉")

@router.callback_query(F.data.startswith("gifts_delete_page:"))
async def gifts_delete_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    total = count_gifts()
    if total == 0:
        await callback.message.edit_text("Пока подарков нет. Но это легко исправить 😉", reply_markup=get_gifts_menu())
        return
    items = list_gifts(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    text = f"🗑 <b>Удаление подарков</b>\nСтраница: <b>{page+1}</b> • Всего: <b>{total}</b>\n\nВыберите подарок:"
    await callback.message.edit_text(text, reply_markup=get_gifts_delete_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")

@router.callback_query(F.data.startswith("gifts_delete_id:"))
async def gifts_delete_id(callback: CallbackQuery):
    _, gid, page = callback.data.split(":")
    gid, page = int(gid), int(page)
    delete_gift(gid)
    await callback.answer("Удалено ✅", show_alert=False)

    total = count_gifts()
    if total == 0:
        await callback.message.edit_text("Все подарки удалены. Свободно дышим и готовим новые! 🌬️", reply_markup=get_gifts_menu())
        return
    page = min(page, max((total - 1) // PAGE_SIZE, 0))
    items = list_gifts(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    text = f"🗑 <b>Удаление подарков</b>\nСтраница: <b>{page+1}</b> • Всего: <b>{total}</b>\n\nВыберите подарок:"
    await callback.message.edit_text(text, reply_markup=get_gifts_delete_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")


# =====================================================================
#                             ПОЛЬЗОВАТЕЛЬ
# =====================================================================

# ----- Отзывы -----
@router.message(F.text == "💬 Отзывы")
async def u_reviews_root(message: Message):
    total = count_reviews()
    caption = (
        "💬 <b>Отзывы</b>\n\n"
        "Живые впечатления наших клиентов — лучше всякой рекламы. "
        "Выберите карточку, чтобы прочитать полностью. 👇"
    )
    items = list_reviews(offset=0, limit=PAGE_SIZE)

    # если нет отзывов — всё равно показываем красивую картинку и текст
    img = _img_path("reviews")
    if img:
        kb = get_user_reviews_keyboard(0, PAGE_SIZE, total, items) if total > 0 else None
        await message.answer_photo(FSInputFile(img), caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        if total == 0:
            await message.answer("✨ Пока отзывов нет. Но совсем скоро здесь появятся истории наших клиентов!", parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=get_user_reviews_keyboard(0, PAGE_SIZE, total, items), parse_mode="HTML")


@router.callback_query(F.data.startswith("u_reviews_page:"))
async def u_reviews_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    total = count_reviews()
    items = list_reviews(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    if not items:
        await callback.answer("Больше отзывов нет. 📚", show_alert=True)
        return
    text = (
        f"💬 <b>Отзывы</b> — страница <b>{page+1}</b>\n\n"
        "Выберите отзыв, чтобы открыть его целиком."
    )
    await callback.message.edit_text(text, reply_markup=get_user_reviews_keyboard(page, PAGE_SIZE, total, items), parse_mode="HTML")

@router.callback_query(F.data.startswith("u_review_id:"))
async def u_review_open(callback: CallbackQuery):
    # u_review_id:{id}:{page}
    try:
        _, rid, page = callback.data.split(":")
        rid, page = int(rid), int(page)
    except Exception:
        await callback.answer("Ошибка данных.", show_alert=True)
        return

    row = get_review_by_id(rid)
    if not row:
        await callback.answer("Отзыв не найден.", show_alert=True)
        return

    _id, author, text, date = row
    msg = f"🧑 <b>{author}</b>\n🗓 {date}\n\n{(text or '').strip()}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data=f"u_reviews_page:{page}")]
    ])

    # Если предыдущее сообщение было фото/документ — у него нет .text, тогда шлём новое
    try:
        if callback.message.text:
            await callback.message.edit_text(msg, reply_markup=kb, parse_mode="HTML")
        else:
            await callback.message.answer(msg, reply_markup=kb, parse_mode="HTML")
    except TelegramBadRequest:
        # Фолбэк, если Telegram ругается
        await callback.message.answer(msg, reply_markup=kb, parse_mode="HTML")



# ----- Услуги -----
@router.message(F.text == "🛠 Услуги")
async def u_services_root(message: Message):
    total = count_services()
    caption = (
        "🛠 <b>Услуги</b>\n\n"
        "Наша экспертиза — ваша сила. Откройте карточку, чтобы узнать детали и посмотреть вложения. 👇"
    )
    items = list_services(offset=0, limit=PAGE_SIZE)

    img = _img_path("services")
    if img:
        kb = get_user_services_keyboard(0, PAGE_SIZE, total, items) if total > 0 else None
        await message.answer_photo(FSInputFile(img), caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        if total == 0:
            await message.answer("✨ Пока услуг нет. Мы уже работаем над тем, чтобы порадовать вас новыми предложениями!", parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=get_user_services_keyboard(0, PAGE_SIZE, total, items), parse_mode="HTML")


# --- Пользователь: Услуги — пагинация ---
@router.callback_query(F.data.startswith("u_services_page:"))
async def u_services_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
    except Exception:
        page = 0
    total = count_services()
    items = list_services(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    if not items:
        await callback.answer("Больше услуг нет. 📘", show_alert=True)
        return

    text = f"🛠 <b>Услуги</b> — страница <b>{page+1}</b>\nВыберите карточку ниже."
    kb = get_user_services_keyboard(page, PAGE_SIZE, total, items)

    # Если текsta нет (например, предыдущее сообщение было с фото/документом) — отправим новое сообщение
    if callback.message.text:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("u_service_id:"))
async def u_service_open(callback: CallbackQuery):
    try:
        _, sid, page = callback.data.split(":")
        sid, page = int(sid), int(page)
    except Exception:
        await callback.answer("Ошибка данных.", show_alert=True)
        return
    row = get_service_by_id(sid)
    if not row:
        await callback.answer("Услуга не найдена.", show_alert=True)
        return
    _id, name, description, file_path = row
    text = f"🛠 <b>{name}</b>\n\n{description}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data=f"u_services_page:{page}")]
    ])
    if file_path and os.path.exists(file_path):
        if _is_image(file_path):
            await callback.message.answer_photo(FSInputFile(file_path), caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.answer_document(FSInputFile(file_path), caption=text, parse_mode="HTML", reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ----- Подарок -----
@router.message(F.text == "🎁 Подарок")
async def u_gifts_root(message: Message):
    total = count_gifts()
    caption = (
        "🎁 <b>Подарки</b>\n\n"
        "Самые тёплые бонусы и спецпредложения. Откройте карточку и заберите своё. 👇"
    )
    items = list_gifts(offset=0, limit=PAGE_SIZE)

    img = _img_path("gifts")
    if img:
        kb = get_user_gifts_keyboard(0, PAGE_SIZE, total, items) if total > 0 else None
        await message.answer_photo(FSInputFile(img), caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        if total == 0:
            await message.answer("✨ Пока подарков нет. Совсем скоро тут будут приятные сюрпризы. 🎀", parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=get_user_gifts_keyboard(0, PAGE_SIZE, total, items), parse_mode="HTML")


# --- Пользователь: Подарки — пагинация ---
@router.callback_query(F.data.startswith("u_gifts_page:"))
async def u_gifts_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
    except Exception:
        page = 0
    total = count_gifts()
    items = list_gifts(offset=page * PAGE_SIZE, limit=PAGE_SIZE)
    if not items:
        await callback.answer("Больше подарков нет. 🎁", show_alert=True)
        return

    text = f"🎁 <b>Подарки</b> — страница <b>{page+1}</b>\nВыберите карточку ниже."
    kb = get_user_gifts_keyboard(page, PAGE_SIZE, total, items)

    if callback.message.text:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("u_gift_id:"))
async def u_gift_open(callback: CallbackQuery):
    try:
        _, gid, page = callback.data.split(":")
        gid, page = int(gid), int(page)
    except Exception:
        await callback.answer("Ошибка данных.", show_alert=True)
        return
    row = get_gift_by_id(gid)
    if not row:
        await callback.answer("Подарок не найден.", show_alert=True)
        return
    _id, name, description, file_path = row
    text = f"🎁 <b>{name}</b>\n\n{description}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data=f"u_gifts_page:{page}")]
    ])
    if file_path and os.path.exists(file_path):
        if _is_image(file_path):
            await callback.message.answer_photo(FSInputFile(file_path), caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.answer_document(FSInputFile(file_path), caption=text, parse_mode="HTML", reply_markup=kb)
    else:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ----- Контакты -----
@router.message(F.text == "📞 Контакты")
async def u_contacts(message: Message):
    caption = (
        "📞 <b>Остаёмся на связи!</b>\n\n"
        "Нажмите на кнопку ниже — и мы уже рядом. Если не ответим сразу, "
        "обязательно вернёмся с лучшим решением. 💬"
    )
    img = _img_path("contacts")
    kb = get_contacts_keyboard(CONTACT_URL, CONTACT_BUTTON_TEXT)

    if img:
        await message.answer_photo(FSInputFile(img), caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        await message.answer(caption, reply_markup=kb, parse_mode="HTML")

