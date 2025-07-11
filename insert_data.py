import asyncio
import aiosqlite






async def insert():
    async with aiosqlite.connect("saints.db") as db:
        await db.execute("""
            INSERT INTO saints (
                day_month,
                name,
                life,
                prayer,
                when_to_pray,
                icon,
                preamble,
                prayer_church_slavonic,
                prayer_rule
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "07-12",
                "Святые первоверховные апостолы Пётр и Павел",
                "Апостолы Пётр и Павел — величайшие проповедники Евангелия, которых Церковь называет первоверховными за особое значение их апостольского служения. Святой Пётр, бывший рыбак, был призван Господом первым из учеников, исповедал Христа Сыном Божиим и стал камнем Церкви. Апостол Павел, бывший гонитель христиан, после обращения ко Христу стал неутомимым миссионером, прошёл множество стран, основал Церкви и написал послания, вошедшие в Новый Завет. Оба приняли мученическую смерть в Риме при императоре Нероне.",
                "Святые апостолы Пётр и Павел, молите Бога о нас!",
                "• при миссионерской деятельности и катехизации; \n• при духовной немощи и страхе перед исповеданием веры; \n• о твёрдости в вере и любви к истине; \n• при борьбе с грехами и страстями; \n• о вдохновении и мудрости в служении и проповеди.",
                "07-12-petr-pavel.jpg",
                "12 июля Церковь празднует память святых первоверховных апостолов Петра и Павла — столпов Церкви Христовой, чьи труды, страдания и вера стали основанием христианской проповеди по всему миру.",
                "Святыи апостоли Петре и Павле, молите Бога о нас.",
                "1. *Осенить себя крестным знамением* и помолчать, вспомнив о своём призвании следовать за Христом.  \n2. *Трижды* произнести:  \n_«Святые апостолы Пётр и Павел, молите Бога о нас»_  \n3. *Молитва:*  \n*Святые апостолы Христовы, Пётр и Павел,* верные ученики, проповедники Евангелия, страдальцы за Истину! Укрепите и нас в следовании за Христом, даруйте мудрость в слове, силу в молитве и любовь к Церкви. Молите Господа о прощении наших согрешений и о спасении душ наших. Аминь.  \n4. *Молитва своими словами* — попроси:  \n– о твёрдости в вере и любви к Евангелию,  \n– о силе для проповеди и служения ближним,  \n– о помощи в духовной борьбе.  \n5. *Завершение:*  \n_Слава Отцу и Сыну и Святому Духу, и ныне и присно, и во веки веков. Аминь._"
        ))

        await db.commit()












asyncio.run(insert())

