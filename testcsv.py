import asyncio
import aiosqlite

async def init_db():
    async with aiosqlite.connect("saints.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS saints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        name TEXT,
        life TEXT
                )
        """)

        await db.commit()

asyncio.run(init_db())

