import discord
from discord.ext import commands
from sys import argv

class Blah:
    """
    Custom addon to make announcements.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def announce(self, ctx, *, inp):
        await self.bot.send_message(self.bot.announcements_channel, inp)

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def speak(self, ctx, channel_destination: str, *, inp):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_message(channel, inp)

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True, pass_context=True)
    async def sendtyping(self, ctx, channel_destination: str):
        channel = ctx.message.channel_mentions[0]
        await self.bot.send_typing(channel)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True, pass_context=True)
    async def dm(self, ctx, channel_destination: str, *, inp):
        dest = ctx.message.mentions[0]
        await self.bot.send_message(dest, inp)

    @commands.command()
    async def event(self):
        embed = discord.Embed(title="Event Information", description="**The 1st Nintendo Homebrew Tournament**", color=discord.Color.dark_red())
        embed.set_thumbnail(url="http://art.gametdb.com/wii/cover/US/RMCE28.png?1431288336")
        embed.set_author(name="Welcome gamers!", url="http://wiki.tockdom.com/wiki/Wiimms_Mario_Kart_Retro_2015-05", icon_url="https://wiimmfi.de/images/wiimmfi-light.svg?=64")
        embed.set_footer(text="dubyadud & FlimFlam69", icon_url="https://cdn.discordapp.com/avatars/186483213701611520/2d1a166be1ea984a4e3d1aed1ce897b4.webp?size=64")
        embed.add_field(name="**How to Join?**", value="Wiims Mario Kart Retro is a custom distributon of Mario Kart Wii (think along the lines of a ROMhack). In order to obtain a copy of this version, users must apply a patch to their own Mario Kart Wii backups using instructions and tools found on [this page](http://wiki.tockdom.com/wiki/Wiimms_Mario_Kart_Retro_2015-05). Once that's done, you can launch the backup using your preferred system (Wii, vWii, or Dolphin) and connect online immideately. You will initially recieve an error message, but that only means you have registered with the servers and entered the 7 day activation period..")
        embed.add_field(name="**When**", value="Registration is now open to everybody on the Discord Server! Registration closes on June 4th and races are slated to begin on June 9th. Users are encouraged to create their copy of Wiimms Mario Kart Retro and register on the Wiimmfi servers asap to ensure that the competition goes smoothly rather than widespread issues on the first day.")
        embed.add_field(name="**Assistance**", value="If you need any kind of help building your own copy of Wiims Mario Kart Retro, please refer to the #event-chat channel.")
        embed.add_field(name="**Other information**", value="We want this to be a fun event! Let's try to keep this civil, friendly, and all tournament based discussion within the #eventchat channel. If you want to play this using Dolphin you must launch the game using your NAND (Dump NAND, extract to folder, set folder in Dolphin).")
        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Blah(bot))
