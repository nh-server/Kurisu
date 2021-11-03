import disnake

from disnake.ext import commands
from disnake.ext.commands import Param

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
    @commands.slash_command()
    async def blah(self, inter):
        pass

    @blah.sub_command()
    async def announce(self, inter, msg: str = Param(desc="Message to announce")):
        """Sends a message to announcements"""
        await self.bot.channels['announcements'].send(msg, allowed_mentions=disnake.AllowedMentions(everyone=True, roles=True))
        await inter.response.send_message("Message send!")

    @blah.sub_command()
    async def speak(self, inter, channel: disnake.TextChannel = Param(desc="Channel to send the message"), msg: str = Param(desc="Message to send")):
        if channel.id in self.speak_blacklist:
            await inter.response.send_message(f'You cannot send a message to {channel.mention}.', ephemeral=True)
            return
        await channel.send(msg, allowed_mentions=disnake.AllowedMentions(everyone=True, roles=True))

    @blah.sub_command()
    async def sendtyping(self, inter, channel: disnake.TextChannel = Param(default=lambda inter: inter.channel, desc="Channel to send the typing event")):
        if channel.id in self.speak_blacklist:
            await inter.response.send_message(f'You cannot send a message to {channel.mention}.', ephemeral=True)
            return
        await channel.trigger_typing()

    @is_staff("Owner")
    @blah.sub_command()
    async def dm(self, inter, msg: str = Param(desc="Message to send"), member: disnake.Member = Param(default=lambda inter: inter.channel, desc="Member to send message")):
        await send_dm_message(member, msg, inter)


def setup(bot):
    bot.add_cog(Blah(bot))
