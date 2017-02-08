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

    async def embed_xkcd_comic(self, comic):
        embed = discord.Embed(title="{}: {}".format(comic.number, comic.getTitle()), url="https://xkcd.com/{}".format(comic.number), color=discord.Color.blue())
        embed.set_image(url=comic.getImageLink())
        embed.set_footer(text=comic.getAltText())
        return embed

    @commands.command()
    async def xkcd(self, comicnum):
        """Show xkcd comic by number. Use "latest" to show the latest comic, or "random" to show a random comic."""
        if comicnum == "latest":
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getLatestComic()))
        elif comicnum == "random":
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getRandomComic()))
        else:
            await self.bot.say("", embed=await self.embed_xkcd_comic(xkcd.getComic(comicnum)))

    async def on_message(self, message):
        # http://stackoverflow.com/questions/839994/extracting-a-url-in-python
        urls = re.findall(r'(https?://\S+)', message.content)
        for url in urls:
            ps = urlparse(url)
            if ps.netloc == "xkcd.com" or ps.netloc == "www.xkcd.com":
                comicnum = ps.path.replace('/', '')
                await self.bot.send_message(message.channel, embed=await self.embed_xkcd_comic(xkcd.getComic(comicnum)))

def setup(bot):
    bot.add_cog(xkcdparse(bot))
