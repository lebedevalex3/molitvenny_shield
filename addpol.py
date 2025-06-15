import asyncio
import aiosqlite

async def add_column():
    async with aiosqlite.connect("saints.db") as db:
        await db.execute("ALTER TABLE saints ADD COLUMN dative_name TEXT;")
        await db.commit()

asyncio.run(add_column())
