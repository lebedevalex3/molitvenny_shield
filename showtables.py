import asyncio
import aiosqlite



async def show_tables():
    async with aiosqlite.connect("saints.db") as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            tables = await cursor.fetchall()
            print("📋 Таблицы в базе данных:")
            for table in tables:
                print("-", table[0])

async def describe_table():
    async with aiosqlite.connect("saints.db") as db:
        async with db.execute("PRAGMA table_info(saints);") as cursor:
            columns = await cursor.fetchall()
            print("📌 Структура таблицы saints:")
            for col in columns:
                cid, name, datatype, notnull, dflt_value, pk = col
                print(f"- {name} ({datatype}) {'PRIMARY KEY' if pk else ''}")


asyncio.run(show_tables())
asyncio.run(describe_table())


