#Importing libraries
import discord
from discord.ext import commands
from sys import argv

class Rules:
    """
    Read da rules.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command()
    async def unban(self):
        """States some stuff about no assistance with bans"""
        await self.bot.say("Please refrain from asking for or giving assistance with unbanning consoles which have been banned from online services.\nReminder: sharing files that allow other users to evade Nintendo issued bans is a bannable offense.")

    @commands.command()
    async def pirate(self):
        """Hey! You can't steal another trainer's Pokémon!"""
        await self.bot.say("Please refrain from asking for or giving assistance with installing or using illegitimately obtained software.")

    @commands.command(hidden=True)
    async def nick(self):
       """Displays the Nickname and Avatar Policy."""
       await self.bot.say("**__Nickname and Avatar Policy:__**\nNicknames are to be kept primarily alphanumeric, to keep them easy to tag and read. In addition, excessively long usernames are unacceptable, as they break up the chat too much.\nIf your username is not, you may request a nickname from a staff member. Otherwise, we may forcibly set one on you.\nAttempts to impersonate another user via nickname and/or avatar change are unacceptable.\nExcessively crude or NSFW usernames or avatars are unacceptable.​")

    @commands.command()
    async def rules(self):
       """Links to 3dshacks.ml."""
       await self.bot.say("Please check <#196618637950451712> or <http://3dshacks.ml> for a full list of rules")

    @commands.command(hidden=True)
    async def r1(self):
       """Displays rule one."""
       await self.bot.say("```1. Keep your conduct and conversation civil. This means, including and limited to:\na) You may disagree with anyone or anything you like, but you should try to keep it to opinions, and not people. Avoid vitriol.\nb) Constant antagonistic behavior is considered uncivil and appropriate action will be taken.\n- This rule is intended purely for the purpose of attempting to prevent flame wars, and is not to be interpreted in a way that disrupts normal conversation.```")

    @commands.command(hidden=True)
    async def r2(self):
       """Displays rule two."""
       await self.bot.say("```2. English is the only language to be spoken on this server.```")

    @commands.command(hidden=True)
    async def r3(self):
       """Displays rule three."""
       await self.bot.say("```3. Support questions are to be asked in #help-and-questions exclusively.```")

    @commands.command(hidden=True)
    async def r4(self):
       """Displays rule four."""
       await self.bot.say("```4. When answering questions in #help-and-questions, remain helpful. Derailing support is impermissible. Remarks that are not helpful will be removed on sight. Continued derailing will constitute further action.```")

    @commands.command(hidden=True)
    async def r5(self):
       """Displays rule five."""
       await self.bot.say("```5. Off-topic discussion is permitted only in #off-topic. This includes political and other strongly opinionated debates. The #voice channel is an exception, when it is active.```")

    @commands.command(hidden=True)
    async def r6(self):
       """Displays rule six."""
       await self.bot.say("```6. Excessively long texts are to be placed on a 'pastebin'-style website such as http://hastebin.com/.```")

    @commands.command(hidden=True)
    async def r7(self):
       """Displays rule seven."""
       await self.bot.say("```7. Repetitive posting is considered spamming and is unacceptable.\na) Asking the same question repeatedly is permitted, but only if you have a reasonable cause to believe you were not purposefully ignored.\nb) Sending a large number of messages in a short period of time ('flooding') is also considered spam. This includes image or link flooding.```")

    @commands.command(hidden=True)
    async def r8(self):
       """Displays rule eight."""
       await self.bot.say("```8. Brigading, bombing, raiding, or otherwise making inaccessible, unusable, or undesirable another server or website is strictly prohibited.```")

    @commands.command(hidden=True)
    async def r9(self):
       """Displays rule nine."""
       await self.bot.say("```9.  User-side scripts / plugins are permitted, provided they do not cause annoyance to the community or have community-accessible triggers.\n- Note that this rule allows for individual triggers, running full on selfbots falls under 'fully automated clients' and must be used in accordance with rule 10.```")

    @commands.command(hidden=True)
    async def r10(self):
       """Displays rule 10."""
       await self.bot.say("```10. Bots and other fully automated clients require explicit written permission from a Discord server owner: ihaveahax or 916253 (Adrian).```")

    @commands.command(hidden=True)
    async def r11(self):
       """Quotes rule 11."""
       await self.bot.say("```11. Illegitimate copies and other copyright violations will not be tolerated. This includes:\n- Sharing full game data, such as .3DS/CCI or CIA files, Sharing 'ticket' files, Sharing titlekeys, linking to any site with the purpose of hosting or providing the former (general encryption keys not associated with piracy are not affected by this).\n- All discussion of piracy is strictly forbidden in help channels. This includes but is not limited to: asking for and giving assistance with piracy, admission of piracy, etc.```")

    @commands.command(hidden=True)
    async def r12(self):
       """Displays rule 12."""
       await self.bot.say("```12. Not-safe-for-work content of any kind is strictly prohibited. This includes gore or other 'shock' content.```")

    @commands.command(hidden=True)
    async def r13(self):
       """Displays rule 13."""
       await self.bot.say("```13. Evading the rules, seeking loopholes, or attempting to stay 'borderline' within the rules, is considered to be breaking the rules.```")

    @commands.command(hidden=True)
    async def r14(self):
       """Displays rule 14."""
       await self.bot.say("```14. Links to other Discord servers are allowed, on the following conditions:\n- You must receive written consent from a staff member.\n- The linked server must not directly violate any of this server's rules.\n- You may not spam advertisement to the server, post the link once and be done.```")

def setup(bot):
    bot.add_cog(Rules(bot))
