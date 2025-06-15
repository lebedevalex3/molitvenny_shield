import aiosqlite
from datetime import datetime

async def init_db():
    async with aiosqlite.connect("saints.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS saints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_month TEXT,
            name TEXT,
            life TEXT,
            prayer TEXT,
            when_to_pray TEXT,
            icon TEXT,
            preamble TEXT,
            prayer_church_slavonic TEXT,
            prayer_rule TEXT
        )
        """)
        await db.commit()

async def get_saints_by_day(day_month: str):
    async with aiosqlite.connect("saints.db") as db:
        cursor = await db.execute("SELECT * FROM saints WHERE day_month = ?", (day_month,))
        return await cursor.fetchall()