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

    async def on_message(self, message):
        # http://stackoverflow.com/questions/839994/extracting-a-url-in-python
        urls = re.findall(r'(https?://\S+)', message.content)
        for url in urls:
            ps = urlparse(url)
            if ps.netloc == "xkcd.com" or ps.netloc == "www.xkcd.com":
                comicnum = ps.path.replace('/', '')
                print(comicnum)
                comic = xkcd.getComic(comicnum)
                embed = discord.Embed(title="{}: {}".format(comicnum, comic.getTitle()), url=url, color=discord.Color.blue())
                embed.set_image(url=comic.getImageLink())
                embed.set_footer(text=comic.getAltText())
                await self.bot.send_message(message.channel, "", embed=embed)

def setup(bot):
    bot.add_cog(xkcdparse(bot))
