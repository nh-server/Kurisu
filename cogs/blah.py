import discord

from cogs.checks import is_staff
from discord.ext import commands


class Blah(commands.Cog):
    """
    Custom Cog to make announcements.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    speak_blacklist = [
        647348710602178560,  # #minecraft-console
        225556031428755456   # #announcements
    ]
    
    @is_staff("OP")
    @commands.command(hidden=True)
    async def announce(self, ctx, *, inp):
        await self.bot.channels['announcements'].send(inp)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def speak(self, ctx, channel: discord.TextChannel, *, inp):
        if channel.id in speak_blacklist:
            await ctx.send(f'You cannot send a message to {channel.mention}.')
            return
        await channel.send(inp)

    @is_staff("OP")
    @commands.command(hidden=True)
    async def sendtyping(self, ctx, channel: discord.TextChannel = None):
        if channel.id in speak_blacklist:
            await ctx.send(f'You cannot send a message to {channel.mention}.')
            return
        if channel is None:
            channel = ctx.channel
        await channel.trigger_typing()

    @is_staff("Owner")
    @commands.command(hidden=True)
    async def dm(self, ctx, member: discord.Member, *, inp):
        try:
            await member.send(inp)
        except (discord.HTTPException, discord.Forbidden):
            await ctx.send("Failed to send dm!")


def setup(bot):
    bot.add_cog(Blah(bot))
