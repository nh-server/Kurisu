import discord
import re
import xkcd
from discord.ext import commands
from sys import argv
from urllib.parse import urlparse

class xkcdparse:
    """
    xkcd parser.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    word_responses = {
        "pointers": 138,
        "sudo": 149,
        "sandwich": 149,
        "compiling": 303,
        "code compiling": 303,
        "bobby tables": 327,
        "little bobby tables": 327,
        "duty calls": 386,
        "security": 538,
        "standards": 927,
        "password": 936,
        "denvercoder9": 979,
        "workflow": 1172,
        "free speech": 1357,
        "screenshot": 1373,
        "tasks": 1425,

    }

    async def embed_xkcd_comic(self, comic):
        embed = discord.Embed(title="{}: {}".format(comic.number, comic.getTitle()), url="https://xkcd.com/{}".format(comic.number), color=discord.Color.blue())
        embed.set_image(url=comic.getImageLink())
        embed.set_footer(text=comic.getAltText())
        return embed

    @commands.command()
    async def xkcd(self, *, comic):
        comic = comic.lower()
        """Show xkcd comic by number. Use "latest" to show the latest comic, or "random" to show a random comic."""
        if comic == "latest":
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getLatestComic()))
        elif comic == "random":
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getRandomComic()))
        elif comic.isdigit():
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getComic(comic)))
        elif comic in self.word_responses:
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getComic(self.word_responses[comic])))
        else:
            await self.bot.say("I can't find that one!")

    # async def on_message(self, message):
    #     # http://stackoverflow.com/questions/839994/extracting-a-url-in-python
    #     urls = re.findall(r'(https?://\S+)', message.content)
    #     for url in urls:
    #         ps = urlparse(url)
    #         if ps.netloc == "xkcd.com" or ps.netloc == "www.xkcd.com":
    #             comicnum = ps.path.replace('/', '')
    #             await self.bot.send_message(message.channel, embed=await self.embed_xkcd_comic(xkcd.getComic(comicnum)))

def setup(bot):
    bot.add_cog(xkcdparse(bot))
