import aiosqlite3
import json


class Manager:
    def __init__(self, bot):
        self.dbcon = bot.holder

    @staticmethod
    def format_args(args: dict) -> str:
        if len(args) < 1:
            return ''
        statement = 'WHERE '
        conditions = []
        for kword, value in args.items():
            conditions.append(f"{kword} = '{value}'")
        return statement + ' AND '.join(conditions)


class WordFilterManager(Manager):
    def __init__(self, bot):
        super().__init__(bot)
        self.kinds = ('piracy tool', 'piracy video', 'piracy tool alert', 'drama', 'unbanning tool', 'piracy site')
        self.filter = {}

    async def load(self):
        for kind in self.kinds:
            self.filter[kind] = [i[0] for i in await self.fetch(kind=kind)]
        print("Loaded word filter")

    async def bulk_load(self):
        with open("wordfilter.json", 'r') as f:
            dict = json.load(f)
            values = []
            for kind in self.kinds:
                if kind in dict:
                    for entry in dict[kind]:
                        values.append(f"('{entry}','{kind}')")
            async with self.dbcon as cur:
                await cur.execute(f"INSERT INTO wordfilter VALUES {','.join(values)}")
            await self.load()

    async def add(self, word: str, kind: str) -> tuple:
        async with self.dbcon as cur:
            try:
                await cur.execute(f'INSERT INTO wordfilter VALUES ("{word}","{kind}")')
            except aiosqlite3.IntegrityError as e:
                print(e)
                return None, None
        await self.load()
        return word, kind

    async def fetch(self, **kwargs) -> tuple:
        cond = self.format_args(kwargs)
        async with self.dbcon as cur:
            await cur.execute(f'SELECT word FROM wordfilter {cond}')
            return await cur.fetchall()

    async def delete(self, word: str):
        if not await self.fetch(word=word):
            return None
        async with self.dbcon as cur:
            await cur.execute(f'DELETE FROM wordfilter WHERE word="{word}"')
        await self.load()
        return word
