import discord

from discord.ext import commands
from utils.checks import is_staff
from utils.utils import send_dm_message


class Blah(commands.Cog):
    """
    Custom Cog to make announcements.
    """
    def __init__(self, bot):
        self.bot = bot

    speak_blacklist = [
        647348710602178560,  # #minecraft-console
    ]

    @is_staff("OP")
    @commands.command()
    async def announce(self, ctx, *, inp):
        await self.bot.channels['announcements'].send(inp, allowed_mentions=discord.AllowedMentions(everyone=True))

    @is_staff("OP")
    @commands.command()
    async def speak(self, ctx, channel: discord.TextChannel, *, inp):
        if channel.id in self.speak_blacklist:
            await ctx.send(f'You cannot send a message to {channel.mention}.')
            return
        await channel.send(inp, allowed_mentions=discord.AllowedMentions(everyone=True))

    @is_staff("OP")
    @commands.command()
    async def sendtyping(self, ctx, channel: discord.TextChannel = None):
        if channel.id in self.speak_blacklist:
            await ctx.send(f'You cannot send a message to {channel.mention}.')
            return
        if channel is None:
            channel = ctx.channel
        await channel.trigger_typing()

    @is_staff("Owner")
    @commands.command()
    async def dm(self, ctx, member: discord.Member, *, inp):
        status = await send_dm_message(member, inp)
        if not status:
            await ctx.send("Failed to send DM!")
        else:
            await ctx.send("Successfully sent DM!")


def setup(bot):
    bot.add_cog(Blah(bot))
