import os
import asyncio
import aiosqlite
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from db import init_db, get_saints_by_day

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
router = Router()
dp.include_router(router)


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
                InlineKeyboardButton(text="📖 Житие", url=f"https://t.me/{me.username}?start=life_{saint_id}"),
                InlineKeyboardButton(text="🕯 Свеча", url=f"https://t.me/{me.username}?start=candle_{saint_id}")
            ],
            [
                InlineKeyboardButton(text="🙏❓ Когда молиться", url=f"https://t.me/{me.username}?start=when_{saint_id}")
            ],
            [
                InlineKeyboardButton(text="📘 Молитвенное правило", url=f"https://t.me/{me.username}?start=rule_{saint_id}")
            ]
        ])

        try:
            # 👇 Отправляем преамбулу отдельно для каждого святого, если она есть
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


@router.message(F.text.startswith("/start"))
async def handle_start(message: Message):
    if message.chat.type != "private":
        return

    parts = message.text.strip().split()
    if len(parts) == 2:
        param = parts[1]
        if "_" not in param:
            await message.answer("❌ Неверная команда.")
            return

        action, saint_id = param.split("_")

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
        elif action == "church":
            await message.answer(f"📜 *Молитва на церковнославянском* ({name}):\n\n{saint[8]}")
        elif action == "rule":
            await message.answer(f"📘 *Краткое молитвенное правило* {dativ}:\n\n{saint[9]}")
        elif action == "when":
            await message.answer(f"📌 *Когда молиться* ({name}):\n\n{saint[5]}")
        elif action == "candle":
            candle_gif = FSInputFile("media/candle.gif")
            await message.answer_animation(animation=candle_gif, caption=f"🕯 Молитвенная свеча поставлена {dativ}.")
        elif action == "ask":
            await message.answer(f"✉️ В будущем тут будет AI-помощник, подбирающий святого по намерению молитвы.")
        else:
            await message.answer("❌ Неизвестная команда.")
    else:
        await message.answer(
            "Привет! Я помогу тебе узнать больше о православных святых. "
            "Нажми на кнопку под интересующим святым в нашем канале."
        )


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())





