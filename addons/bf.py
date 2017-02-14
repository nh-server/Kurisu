import discord
import getch
from discord.ext import commands
from sys import argv

class bf:
    """
    parses a certain esoteric language.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    def cleanup(self, code):
        return "".join(x for x in code if x in ['.', ',', '[', ']', '<', '>', '+', '-'])

    def buildbracemap(self, code):
        temp_bracestack, bracemap = [], {}

        for position, command in enumerate(code):
            if command == "[": temp_bracestack.append(position)
            if command == "]":
                start = temp_bracestack.pop()
                bracemap[start] = position
                bracemap[position] = start
        return bracemap

    # based on https://github.com/pocmo/Python-Brainfuck/blob/master/brainfuck.py
    @commands.command()
    async def bf(self, code):
        """Interpret something that messes with your brain."""
        code     = self.cleanup(list(code))
        bracemap = self.buildbracemap(code)

        cells, codeptr, cellptr = [0], 0, 0

        output = ""

        while codeptr < len(code):
            command = code[codeptr]

            if command == ">":
                cellptr += 1
                if cellptr == len(cells): cells.append(0)

            if command == "<":
                cellptr = 0 if cellptr <= 0 else cellptr - 1

            if command == "+":
                cells[cellptr] = cells[cellptr] + 1 if cells[cellptr] < 255 else 0

            if command == "-":
                cells[cellptr] = cells[cellptr] - 1 if cells[cellptr] > 0 else 255

            if command == "[" and cells[cellptr] == 0: codeptr = bracemap[codeptr]
            if command == "]" and cells[cellptr] != 0: codeptr = bracemap[codeptr]
            if command == ".": output += chr(cells[cellptr])
            if command == ",": cells[cellptr] = ord(getch.getch())

            codeptr += 1

        await self.bot.say(output)

def setup(bot):
    bot.add_cog(bf(bot))
