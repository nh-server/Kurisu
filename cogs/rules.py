import discord

from utils import crud
from utils.checks import is_staff
from discord.ext import commands


class Rules(commands.Cog, command_attrs=dict()):
    """
    Read da rules.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_all_ready()
        self.nh_emoji = discord.utils.get(self.bot.guild.emojis, name="nintendo_homebrew")
        self.logo_3ds = discord.utils.get(self.bot.guild.emojis, name="3dslogo")
        self.logo_wiiu = discord.utils.get(self.bot.guild.emojis, name="wiiulogo")
        self.logo_switch = discord.utils.get(self.bot.guild.emojis, name="switchlogo")
        self.init_rules()

    async def simple_embed(self, ctx, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await ctx.send(embed=embed)

    def init_rules(self):
        self.rules_dict = {
            1: "Be nice to each other. It's fine to disagree, it's not fine to insult or attack other people.",
            2: "This is an English-speaking server, so please speak English to keep communication simple.",
            3: "Keep 3DS, Wii U, and Switch support questions to the assistance channels.\n • Don't ask how to bypass network restrictions in place by Nintendo or game developers. This includes bypassing console bans.",
            4: "Don't ask to ask, just ask. Just post your question instead of asking if you can and you will get an answer faster.\n • Add details when asking. \"x doesn't work\" will slow down help.",
            5: "Don't spam. Don't post your question twice unless you fully believe you were not intentionally ignored.\n • For excessively long text, use a service like <https://hastebin.com/>.",
            6: "Remain mindful and polite when asking or answering questions in the assistance channels. Derailing support or otherwise causing issues will get your access removed.",
            7: "Don't brigade, raid, or otherwise attack other people or communities. Don't discuss participation in these attacks. This may warrant an immediate permanent ban.",
            8: "One account per user. Bots/fully automated clients run by users are not allowed. Alternate accounts will have access removed. If you are switching accounts, please remove your original from the server.",
            9: "User-side scripts are fine if they are only accessible by you and are not annoying. Community-accessible triggers on a user account are a violation of the Discord Terms of Service.",
            10: "Not-safe-for-work content (including gore, and other \"shock\" content) is prohibited.\nAdditionally hornyposting is heavily discouraged in all the channels.",
            11: "The Piracy rule: Don't... \n• ask how to pirate games\n • share full game data\n • mention piracy sites and tools by name\n • share game tickets and titlekeys\n • ask to share direct messages to help with piracy\n • discuss piracy in the assistance channels\n • in general commit copyright violations",
            12: "Don't post other people's personal information, including social media accounts with this. This may warrant an immediate ban.",
            13: "Ask a staff member before advertising in our server or posting invite links to things like servers on Discord, Skype groups, etc.",
            14: f"Off-topic content goes to {self.bot.channels['off-topic'].mention}. Keep low-quality content like memes out. There is a channel for that, use \".togglechannel elsewhere\" to get access.",
            15: f"Voice and music commands and other random/contextless command usage belong in {self.bot.channels['voice-and-music'].mention} and {self.bot.channels['bot-cmds'].mention} respectively.",
            16: "Trying to evade, look for loopholes, or stay borderline within the rules will be treated as breaking them.",
            17: "With regard to all of the recent Nintendo related leaks that have been occurring, and with regard to leaks of intellectual property of **any** company, __**Do Not**__:\n • ask how to download the leaked content\n • share leaked content or links to leaked content\n • discuss the contents of any leaks, link to discussions of any leaks elsewhere, or suggest or otherwise imply how someone may come across discussion or downloads of leaked content\nViolation of this rule will result in appropriate action being taken by staff. Repeated violation __**will**__ result in an irrevocable ban."
        }

        self.rules_intro = f"""{str(self.nh_emoji)} __**Welcome to Nintendo Homebrew!**__
We're the place to come to for hacking & homebrew on Nintendo's video game consoles, like the Nintendo 3DS, Wii U, and Nintendo Switch. Get assistance with setting up or using homebrew, find news on the latest developments, discuss about what you're making, and more.
     
Be sure you read the following information before participating, especially rules. Not reading them is not an excuse for breaking them!
     
**Attempting to start drama is reason enough for a ban on sight.**
    
**By participating in this server, you acknowledge that user data (including messages, user IDs, user tags) will be collected and logged for moderation purposes. If you disagree with this collection, please leave the server immediately.**\n📑 __*Rules*__\n"""

        self.staff_action = """🔨 __*Staff Action*__
Breaking these rules will result in appropriate measures taken by the staff.
If staff say something is final, it is final and is not up for debate. Staff instruction is to be followed."""

        self.mod_list = f"""🛠️ __*Mod List*__
**Please do not send a direct message unless asked. General questions should go to {self.bot.channels['3ds-assistance-1'].mention}, {self.bot.channels['3ds-assistance-2'].mention}, {self.bot.channels['wiiu-assistance'].mention}, or {self.bot.channels['switch-assistance-1'].mention} channels.
Please contact @NH Mod-Mail if you need to get in touch with the staff team.**\n\n"""

        self.helper_list = """🤝 __*Helper List*__
**Please do not send a direct message unless asked. General questions should go to #3ds-assistance-1, #3ds-assistance-2, #wiiu-assistance, #switch-assistance, or #legacy-systems channels.
Please contact @NH Mod-Mail if you need to get in touch with the staff team. Mod-Mail is NOT FOR GETTING HELP WITH HACKING.**\n"""

        self.nickname_policy = """🏷️ __*Username/Nickname and Avatar policy*__
Usernames are to be kept primarily alphanumeric, to keep them easy to tag and read. Excessively long usernames are not acceptable. Usernames and avatars that are annoying, offensive, inappropriate ("nsfw"), and/or disruptive to others are also not allowed.
Usernames that go against these rules will be assigned a nickname. Users can request a specific nickname that follows these rules.
If the username disrupts the general chat flow, pings included, the user will be asked to change it. Refusal will result in a kick from the server.
Users with avatars against these rules will be asked to change them or be kicked from the server.
Blank names and avatars are considered disruptive and are not allowed."""

        self.useful_commands = """💻 __*Useful commands*__
A few commands may be useful for you to get information faster. Random command usage should be in #bot-cmds.
• `.err <errcode>` - Show information based on Nintendo error codes.
• ex: `.err 022-2501`
• ex: `.err 199-9999`
• ex: `.err 2001-0125`
• ex: `.err 0xD960D02B` (0x not required)
• `.help Assistance` - List assistance-related commands. These can have useful information.
• `.help` - List all the other available commands."""

        self.extra = f"""While we appreciate everyone who boosts the server **IT DOES NOT MAKE YOU EXEMPT FROM THE RULES.** We've given booster reaction perms in {self.bot.channels['off-topic'].mention}, {self.bot.channels['elsewhere'].mention}, and {self.bot.channels['nintendo-discussion'].mention}, you can also stream in the Streaming gamer voice channel, and change your nick once every 6hrs using a bot command in your DM with {self.bot.guild.me.mention},  as a thank you for boosting the server.
📨 Invitation link This is a permanent invitation link to the server!
https://discord.gg/C29hYvh"""

    @is_staff('SuperOP')
    @commands.command(hidden=False)
    async def updaterules(self, ctx):
        """Updates the rules in Welcome and Rules"""
        channel = self.bot.channels['welcome-and-rules']
        async for message in channel.history():
            await message.delete()
        await channel.send(self.rules_intro)
        for number, rule in self.rules_dict.items():
            await channel.send(f"**{number}**. {rule}\n")
        await channel.send(self.staff_action)
        staff = [f"<@{staff.id}>" for staff in await crud.get_staff_all()]
        await channel.send(self.mod_list + '\n'.join(staff))
        helpers = [helper for helper in await crud.get_helpers() if helper.position == 'Helper']
        helpers_3ds = [f"<@{helper.id}>" for helper in helpers if helper.console == '3DS']
        helpers_wiiu = [f"<@{helper.id}>" for helper in helpers if helper.console == 'WiiU']
        helpers_legacy = [f"<@{helper.id}>" for helper in helpers if helper.console == 'Legacy']
        helpers_switch = [f"<@{helper.id}>" for helper in helpers if helper.console == 'Switch']
        await channel.send(self.helper_list)
        await channel.send(f"{str(self.logo_3ds)}  Nintendo 3DS\n" + '\n'.join(helpers_3ds))
        await channel.send(f"{str(self.logo_wiiu)}:  Wii U\n" + '\n'.join(helpers_wiiu))
        await channel.send(f"{str(self.logo_switch)}  Nintendo Switch\n" + '\n'.join(helpers_switch))
        await channel.send("Legacy\n" + '\n'.join(helpers_legacy))
        await channel.send(self.nickname_policy)
        await channel.send(self.useful_commands)
        await channel.send(self.extra)
        await ctx.send("Updated rules successfully!")

    @commands.command(hidden=False)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def consoleban(self, ctx):
        """States some stuff about no assistance with bans"""
        await ctx.send("Please refrain from asking for or giving assistance with unbanning consoles which have been banned from online services.\nReminder: sharing files that allow other users to evade Nintendo issued bans is a bannable offense.")

    @commands.command(aliases=['r11'], hidden=False)
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pirate(self, ctx):
        """Hey! You can't steal another trainer's Pokémon!"""
        await ctx.send("Please refrain from asking for or giving assistance with installing, using, or obtaining pirated software.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nick(self, ctx):
        """Displays the Nickname and Avatar Policy."""
        await ctx.send("🏷 ___Username/Nickname and Avatar policy___\n"
                       "Usernames are to be kept primarily alphanumeric, to keep them easy to tag and read. Excessively long usernames are not acceptable. Usernames and avatars that are annoying, offensive, inappropriate (\"nsfw\"), and/or disruptive to others are also not allowed.\n"
                       "Usernames that go against these rules will be assigned a nickname. Users can request a specific nickname that follows these rules by asking in <#270890866820775946> or by sending a direct message to <@333857992170536961>.\n"
                       "Users with avatars against these rules will be asked to change them or be kicked from the server.")

    @commands.command(hidden=False)
    async def rules(self, ctx):
        """Links to the welcome-and-rules channel."""
        await ctx.send(f"Please check {self.bot.channels['welcome-and-rules'].mention} for a full list of rules")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r1(self, ctx):
        """Displays rule 1."""
        await self.simple_embed(ctx, self.rules[1], title="Rule 1")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r2(self, ctx):
        """Displays rule 2."""
        await self.simple_embed(ctx, self.rules[2], title="Rule 2")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r3(self, ctx):
        """Displays rule 3."""
        await self.simple_embed(ctx, self.rules[3], title="Rule 3")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r4(self, ctx):
        """Displays rule 4."""
        await self.simple_embed(ctx, self.rules[4], title="Rule 4")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r5(self, ctx):
        """Displays rule 5."""
        await self.simple_embed(ctx, self.rules[5], title="Rule 5")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r6(self, ctx):
        """Displays rule 6."""
        await self.simple_embed(ctx, self.rules[6], title="Rule 6")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r7(self, ctx):
        """Displays rule 7."""
        await self.simple_embed(ctx, self.rules[7], title="Rule 7")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r8(self, ctx):
        """Displays rule 8."""
        await self.simple_embed(ctx, self.rules[8], title="Rule 8")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r9(self, ctx):
        """Displays rule 9."""
        await self.simple_embed(ctx, self.rules[9], title="Rule 9")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r10(self, ctx):
        """Displays rule 10."""
        await self.simple_embed(ctx, self.rules[10], title="Rule 10")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def realr11(self, ctx):
        """Displays rule 11."""
        await self.simple_embed(ctx, self.rules[11] +
        "If you simply need to tell someone to not ask about piracy, consider `.pirate` instead. `.r11` was changed to match `.pirate` due to its large embed.", title="Rule 11")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r12(self, ctx):
        """Displays rule 12."""
        await self.simple_embed(ctx, self.rules[12], title="Rule 12")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r13(self, ctx):
        """Displays rule 13."""
        await self.simple_embed(ctx, self.rules[13], title="Rule 13")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r14(self, ctx):
        """Displays rule 14."""
        await self.simple_embed(ctx, self.rules[14], title="Rule 14")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r15(self, ctx):
        """Displays rule 15."""
        await self.simple_embed(ctx, self.rules[15], title="Rule 15")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r16(self, ctx):
        """Displays rule 16."""
        await self.simple_embed(ctx, self.rules[16], title="Rule 16")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r17(self, ctx):
        """Displays rule 17."""
        await self.simple_embed(ctx, self.rules[17], title="Rule 17")


def setup(bot):
    bot.add_cog(Rules(bot))
