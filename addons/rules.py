import discord
from discord.ext import commands

class Rules:
    """
    Read da rules.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def simple_embed(self, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await self.bot.say("", embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def consoleban(self):
        """States some stuff about no assistance with bans"""
        await self.bot.say("Please refrain from asking for or giving assistance with unbanning consoles which have been banned from online services.\nReminder: sharing files that allow other users to evade Nintendo issued bans is a bannable offense.")

    @commands.command(aliases=['r11'])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pirate(self):
        """Hey! You can't steal another trainer's Pokémon!"""
        await self.bot.say("Please refrain from asking for or giving assistance with installing or using illegitimately obtained software.")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nick(self):
        """Displays the Nickname and Avatar Policy."""
        await self.bot.say("🏷 ___Username/Nickname and Avatar policy___\n"
                           "Usernames are to be kept primarily alphanumeric, to keep them easy to tag and read. Excessively long usernames are not acceptable. Usernames and avatars that are annoying, offensive, inappropriate (\"nsfw\"), and/or disruptive to others are also not allowed.\n"
                           "Usernames that go against these rules will be assigned a nickname. Users can request a specific nickname that follows these rules by asking in <#270890866820775946> or by sending a direct message to <@333857992170536961>.\n"
                           "Users with avatars against these rules will be asked to change them or be kicked from the server.")

    @commands.command()
    async def rules(self):
        """Links to rules website."""
        await self.bot.say("Please check {} for a full list of rules".format(self.bot.welcome_channel.mention))

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r1(self):
        """Displays rule 1."""
        await self.simple_embed("Be nice to each other. It's fine to disagree, it's not fine to insult or attack other people.", title="Rule 1")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r2(self):
        """Displays rule 2."""
        await self.simple_embed("This is an English-speaking server, so please speak English to keep communication simple.", title="Rule 2")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r3(self):
        """Displays rule 3."""
        await self.simple_embed("Keep 3DS and Wii U support questions to the assistance channels.\n"
                                    "• Don't ask how to bypass network restrictions in place by Nintendo or game developers. This includes bypassing console bans.", title="Rule 3")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r4(self):
        """Displays rule 4."""
        await self.simple_embed("If you would like assistance, please directly ask your question or concern. You don't need to ask to ask.\n"
                                    " • Please remember to be detailed when asking. Being vague, like \"x doesn't work\" makes things harder for everyone.", title="Rule 4")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r5(self):
        """Displays rule 5."""
        await self.simple_embed("Don't spam. Don't post your question twice unless you fully believe you were not intentionally ignored.\n"
                                    " • For excessively long text, use a service like https://hastebin.com.", title="Rule 5")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r6(self):
        """Displays rule 6."""
        await self.simple_embed("Remain mindful and polite when asking or answering questions in the assistance channels. Derailing support or otherwise causing issues will get your access removed.", title="Rule 6")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r7(self):
        """Displays rule 7."""
        await self.simple_embed("Don't brigade, raid, or otherwise attack other people or communities. Don't discuss participation in these attacks. This may warrant an immediate permanent ban.", title="Rule 7")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r8(self):
        """Displays rule 8."""
        await self.simple_embed("One account per user. Bots/fully automated clients run by users are not allowed. Alternate accounts will have access removed. If you are switching accounts, please remove your original from the server.", title="Rule 8")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r9(self):
        """Displays rule 9."""
        await self.simple_embed("User-side scripts are fine if they are only accessible by you and are not annoying. Community-accessible triggers on a user account are a violation of the Discord Terms of Service.", title="Rule 9")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r10(self):
        """Displays rule 10."""
        await self.simple_embed("Not-safe-for-work content (including gore and other \"shock\" content) is prohibited.", title="Rule 10")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def realr11(self):
        """Displays rule 11."""
        await self.simple_embed("The Piracy rule: Don't...\n"
                                    " • ask how to pirate games\n"
                                    " • share full game data\n"
                                    " • mention piracy sites and tools by name\n"
                                    " • share game tickets and titlekeys\n"
                                    " • ask to share direct messages to help with piracy\n"
                                    " • discuss piracy in the assistance channels\n"
                                    " • in general commit copyright violations\n\n"

                                    "If you simply need to tell someone to not ask about piracy, consider `.pirate` instead. `.r11` was changed to match `.pirate` due to its large embed.", title="Rule 11")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r12(self):
        """Displays rule 12."""
        await self.simple_embed("Don't post other people's personal information, including social media accounts with this. This may warrant an immediate ban.", title="Rule 12")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r13(self):
        """Displays rule 13."""
        await self.simple_embed("Ask a staff member before advertising in our server or posting invite links to things like servers on Discord, Skype groups, etc.", title="Rule 13")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r14(self):
        """Displays rule 14."""
        await self.simple_embed("Off-topic content goes to {}. Keep low-quality content like memes out.".format(self.bot.offtopic_channel.mention), title="Rule 14")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r15(self):
        """Displays rule 15."""
        await self.simple_embed("Voice and music commands and other random/contextless command usage belong in {} and {} respectively.".format(self.bot.voiceandmusic_channel.mention, self.bot.botcmds_channel.mention), title="Rule 15")

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r16(self):
        """Displays rule 16."""
        await self.simple_embed("Trying to evade, look for loopholes, or stay borderline within the rules will be treated as breaking them.", title="Rule 16")

def setup(bot):
    bot.add_cog(Rules(bot))
