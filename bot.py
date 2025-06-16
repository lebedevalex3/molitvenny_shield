import os
import asyncio
import random
import aiosqlite
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message, FSInputFile, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from db import init_db, get_saints_by_day

# --- Настройки окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ENV = os.getenv("ENV", "prod")
PROD_CHANNEL_ID = os.getenv("PROD_CHANNEL_ID")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")
CHANNEL_ID = TEST_CHANNEL_ID if ENV == "test" else PROD_CHANNEL_ID
BOT_USERNAME = os.getenv("BOT_USERNAME")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Группировка категорий с ключами (для коротких callback_data) ---
gratitude_structure = {
    "close": ["👨‍👩‍👧‍👦 Семья", "👶 Дети", "🤝 Друзья", "🧙‍♂️ Наставники"],
    "spiritual": ["🕊️ Вера", "🛐 Святые", "🤲 Прощение", "🌟 Божье водительство"],
    "daily": ["🌳 Природа", "🏡 Дом", "💪 Здоровье", "🌞 Каждый день", "🍞 Хлеб насущный"],
    "special": ["❤️ Любовь", "🤗 Помощь в трудностях", "🧪 Уроки и испытания", "🎉 Радость"]
}

category_titles = {
    "close": "📂 Близкие",
    "spiritual": "✝ Духовное",
    "daily": "🌿 Повседневное",
    "special": "🎁 Особые случаи"
}

# --- /start gratitude ---
@router.message(F.text.startswith("/start gratitude"))
async def handle_start_gratitude(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category_titles[key], callback_data=f"gratitude_cat:{key}")]
        for key in gratitude_structure
    ])
    await message.answer("Выберите основную категорию благодарности:", reply_markup=keyboard)

# --- Обработка кнопок благодарности ---
@router.callback_query(F.data.startswith("gratitude_cat:"))
async def handle_gratitude_category(callback: CallbackQuery):
    category_key = callback.data.split(":")[1]
    subcategories = gratitude_structure.get(category_key, [])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=sub, callback_data=f"gratitude_sub:{category_key}:{i}")]
        for i, sub in enumerate(subcategories)
    ])
    title = category_titles.get(category_key, "Категория")
    await callback.message.edit_text(f"🔸 {title}\nВыберите подкатегорию:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("gratitude_sub:"))
async def handle_gratitude_subcategory(callback: CallbackQuery):
    _, category_key, index_str = callback.data.split(":")
    index = int(index_str)
    subcategory_name = gratitude_structure[category_key][index]
    category_full = category_titles[category_key]

    async with aiosqlite.connect("gratitude.db") as db:
        cursor = await db.execute(
            "SELECT text FROM gratitude WHERE category = ? AND subcategory = ?",
            (category_full, subcategory_name)
        )
        results = await cursor.fetchall()

    if results:
        text = random.choice(results)[0]
        await callback.message.edit_text(f"✨ {text}")
    else:
        await callback.message.edit_text("🙏 Пока нет благодарностей в этой подкатегории.")
    await callback.answer()

# --- Пост с кнопкой (в канал) ---
@router.message(F.text == "/post_gratitude_button")
async def post_gratitude_button(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🙏 Учимся благодарить",
            url=f"https://t.me/{BOT_USERNAME}?start=gratitude"
        )]
    ])
    await bot.send_message(CHANNEL_ID, "✨ Нужны слова благодарности? Нажмите кнопку ниже:", reply_markup=keyboard)
    await message.answer("✅ Кнопка опубликована в канал.")

# --- Публикация святых ---
@router.message(F.text.startswith("/post"))
async def handle_post_command(message: Message):
    if message.chat.type != "private":
        await message.reply("⛔ Эта команда работает только в личных сообщениях.")
        return
    try:
        _, day = message.text.strip().split(" ")
    except ValueError:
        await message.reply("Формат: /post MM-DD (например: /post 06-15)")
        return
    saints = await get_saints_by_day(day)
    if not saints:
        await message.reply("⛔ На эту дату в базе нет святых.")
        return
    me = await bot.get_me()
    for saint in saints:
        saint_id = saint[0]
        name = saint[2]
        life = saint[3]
        prayer = saint[4]
        when_to_pray = saint[5]
        icon = saint[6]
        preamble = saint[7]
        prayer_church_slavonic = saint[8]
        prayer_rule = saint[9]
        dativ = saint[10] if len(saint) > 10 else name
        image_path = f"images/{icon}"
        caption = f"🕊️ *{name}*\n\n🙏 {prayer}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Житие", url=f"https://t.me/{BOT_USERNAME}?start=life_{saint_id}"),
                InlineKeyboardButton(text="🕯 Свеча", url=f"https://t.me/{BOT_USERNAME}?start=candle_{saint_id}")
            ],
            [
                InlineKeyboardButton(text="🙏❓ Когда молиться", url=f"https://t.me/{BOT_USERNAME}?start=when_{saint_id}")
            ],
            [
                InlineKeyboardButton(text="📘 Молитвенное правило", url=f"https://t.me/{BOT_USERNAME}?start=rule_{saint_id}")
            ]
        ])
        try:
            if preamble:
                await bot.send_message(CHANNEL_ID, f"📜{preamble}")
            if os.path.exists(image_path):
                photo = FSInputFile(image_path)
                await bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            await bot.send_message(chat_id=CHANNEL_ID, text=f"⚠️ Ошибка при отправке изображения: {e}")
    await message.reply("✅ Публикация завершена.")

# --- /start ---
@router.message(F.text.startswith("/start"))
async def handle_start(message: Message):
    if message.chat.type != "private":
        return

    parts = message.text.strip().split()

    if len(parts) == 2:
        param = parts[1]

        if "_" in param:
            action, saint_id = param.split("_", 1)

            async with aiosqlite.connect("saints.db") as db:
                cursor = await db.execute("SELECT * FROM saints WHERE id = ?", (saint_id,))
                saint = await cursor.fetchone()

            if not saint:
                await message.answer("❌ Святой не найден.")
                return

            name = saint[2]
            dativ = saint[10] if len(saint) > 10 else name

            if action == "life":
                await message.answer(f"📖 *Житие* {name}:\n\n{saint[3]}")
            elif action == "candle":
                gif = FSInputFile("media/candle.gif")
                await message.answer_animation(gif, caption=f"🕯 Молитвенная свеча поставлена {dativ}.")
            elif action == "when":
                await message.answer(f"📌 *Когда молиться* ({name}):\n\n{saint[5]}")
            elif action == "rule":
                await message.answer(f"📘 *Молитвенное правило* {dativ}:\n\n{saint[9]}")
            else:
                await message.answer("❌ Неизвестная команда.")
        elif param == "gratitude":
            # запускаем интерфейс благодарности
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=category_titles[key], callback_data=f"gratitude_cat:{key}")]
                for key in gratitude_structure
            ])
            await message.answer("Выберите основную категорию благодарности:", reply_markup=keyboard)
        else:
            await message.answer("❌ Неизвестная команда.")
    else:
        await message.answer(
            "Привет! Я помогу тебе узнать больше о православных святых.\n"
            "Или нажми на кнопку «🙏 Учимся благодарить» и начни с благодарности."
        )
# --- MAIN ---
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
