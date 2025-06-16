import aiosqlite
import asyncio

async def init_gratitude_db():
    async with aiosqlite.connect("gratitude.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS gratitude (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,      -- Основная категория (напр. "Близкие")
                subcategory TEXT,   -- Подкатегория (напр. "Семья")
                text TEXT           -- Текст благодарности
            );
        """)
        await db.commit()

asyncio.run(init_gratitude_db())