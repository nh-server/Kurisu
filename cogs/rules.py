import discord

from utils import crud
from utils.checks import is_staff
from utils.utils import paginate_message
from discord.ext import commands


class Rules(commands.Cog):
    """
    Read da rules.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_all_ready()
        self.nh_emoji = discord.utils.get(self.bot.guild.emojis, name="nintendo_homebrew") or "⁉"
        self.logo_3ds = discord.utils.get(self.bot.guild.emojis, name="3dslogo") or "⁉"
        self.logo_wiiu = discord.utils.get(self.bot.guild.emojis, name="wiiulogo") or "⁉"
        self.logo_switch = discord.utils.get(self.bot.guild.emojis, name="switchlogo") or "⁉"
        await self.init_rules()

    async def simple_embed(self, ctx, text, title="", color=discord.Color.default()):
        embed = discord.Embed(title=title, color=color)
        embed.description = text
        await ctx.send(embed=embed)

    async def init_rules(self):
        await self.load_rules()

        self.rules_intro = f"""{str(self.nh_emoji)} __**Welcome to Nintendo Homebrew!**__
We're the place to come to for hacking & homebrew on Nintendo's video game consoles, like the Nintendo 3DS, Wii U, and Nintendo Switch. Get assistance with setting up or using homebrew, find news on the latest developments, discuss about what you're making, and more.

Be sure you read the following information before participating, especially rules. Not reading them is not an excuse for breaking them!

**Attempting to start drama is reason enough for a ban on sight.**

**By participating in this server, you acknowledge that user data (including messages, user IDs, user tags) will be collected and logged for moderation purposes. If you disagree with this collection, please leave the server immediately.**\n📑 __*Rules*__\n"""

        self.staff_action = """🔨 __*Staff Action*__
Breaking these rules will result in appropriate measures taken by the staff, at the discretion of the individual staff member.
If staff say something is final, it is final and is not up for debate.
Staff instruction is to be followed; refusal to do so may result in moderation action taken against you.
"""

        self.mod_list = f"""🛠️ __*Mod List*__
**Please do not send a direct message unless asked. General questions should go to {self.bot.channels['3ds-assistance-1'].mention}, {self.bot.channels['3ds-assistance-2'].mention}, {self.bot.channels['wiiu-assistance'].mention}, {self.bot.channels['switch-assistance-1'].mention}, {self.bot.channels['switch-assistance-2'].mention} or {self.bot.channels['legacy-systems'].mention} channels.
Please contact <@!333857992170536961> if you need to get in touch with the staff team.**\n\n"""

        self.helper_list = f"""🤝 __*Helper List*__
**Please do not send a direct message unless asked. General questions should go to {self.bot.channels['3ds-assistance-1'].mention}, {self.bot.channels['3ds-assistance-2'].mention}, {self.bot.channels['wiiu-assistance'].mention}, {self.bot.channels['switch-assistance-1'].mention}, {self.bot.channels['switch-assistance-2'].mention} or {self.bot.channels['legacy-systems'].mention} channels.
Please contact <@!333857992170536961> if you need to get in touch with the staff team. Mod-Mail is NOT FOR GETTING HELP WITH HACKING.**\n"""

        self.nickname_policy = """🏷️ __*Username/Nickname and Avatar policy*__
Usernames are to be kept primarily alphanumeric, to keep them easy to tag and read. Excessively long usernames are not acceptable. Usernames and avatars that are annoying, offensive, inappropriate ("nsfw"), and/or disruptive to others are also not allowed.
Usernames that go against these rules will be assigned a nickname. Users can request a specific nickname that follows these rules.
If the username disrupts the general chat flow, pings included, the user will be asked to change it. Refusal will result in a kick from the server.
Users with avatars against these rules will be asked to change them or be kicked from the server.
Blank names and avatars are considered disruptive and are not allowed."""

        self.useful_commands = f"""💻 __*Useful commands*__
A few commands may be useful for you to get information faster. Random command usage should be in {self.bot.channels['bot-cmds'].mention}.
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

    async def load_rules(self):
        self.rules_dict = {}
        for rule in await crud.get_rules():
            self.rules_dict[rule.id] = rule.description

    @is_staff('SuperOP')
    @commands.command()
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
        await channel.send(f"{str(self.logo_wiiu)}  Wii U\n" + '\n'.join(helpers_wiiu))
        await channel.send(f"{str(self.logo_switch)}  Nintendo Switch\n" + '\n'.join(helpers_switch))
        await channel.send("Legacy\n" + '\n'.join(helpers_legacy))
        await channel.send(self.nickname_policy)
        await channel.send(self.useful_commands)
        await channel.send(self.extra)
        await ctx.send("Updated rules successfully!")

    @is_staff('SuperOP')
    @commands.group()
    async def rule(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @rule.command(name='add')
    async def add_rule(self, ctx, number: int, *, description: str):
        """Adds or edits a current rule"""
        if await crud.get_rule(number):
            await crud.edit_rule(number, description)
            await ctx.send(f"Rule {number} edited successfully!")
        else:
            await crud.add_rule(number, description)
            await ctx.send(f"Rule {number} added successfully!")
        await self.load_rules()

    @rule.command(name='delete')
    async def delete_rule(self, ctx, number: int):
        if await crud.get_rule(number):
            await crud.delete_rule(number)
            await ctx.send(f"Rule {number} deleted successfully!")
            await self.load_rules()
        else:
            await ctx.send(f"There is no rule {number}!")

    @rule.command(name='list')
    async def list_rules(self, ctx):
        if self.rules_dict:
            rules = [f"**{number}**. {rule}\n" for number, rule in self.rules_dict.items()]
            for page in paginate_message("".join(rules), suffix='', prefix='').pages:
                await ctx.send(page)
        else:
            await ctx.send("There are no rules!")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def consoleban(self, ctx):
        """States some stuff about no assistance with bans"""
        await ctx.send("Please refrain from asking for or giving assistance with unbanning consoles which have been banned from online services.\nReminder: sharing files that allow other users to evade Nintendo issued bans is a bannable offense.")

    @commands.command(aliases=['r11'])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def pirate(self, ctx):
        """Hey! You can't steal another trainer's Pokémon!"""
        await ctx.send("Please refrain from asking for or giving assistance with installing, using, or obtaining pirated software.")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def nick(self, ctx):
        """Displays the Nickname and Avatar Policy."""
        await ctx.send(f"🏷 ___Username/Nickname and Avatar policy___\n"
                       f"Usernames are to be kept primarily alphanumeric, to keep them easy to tag and read. Excessively long usernames are not acceptable. Usernames and avatars that are annoying, offensive, inappropriate (\"nsfw\"), and/or disruptive to others are also not allowed.\n"
                       f"Usernames that go against these rules will be assigned a nickname. Users can request a specific nickname that follows these rules by asking in {self.bot.channels['meta'].mention} or by sending a direct message to <@333857992170536961>.\n"
                       f"Users with avatars against these rules will be asked to change them or be kicked from the server.")

    @commands.command()
    async def rules(self, ctx):
        """Links to the welcome-and-rules channel."""
        await ctx.send(f"Please check {self.bot.channels['welcome-and-rules'].mention} for a full list of rules")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r1(self, ctx):
        """Displays rule 1."""
        await self.simple_embed(ctx, self.rules_dict[1], title="Rule 1")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r2(self, ctx):
        """Displays rule 2."""
        await self.simple_embed(ctx, self.rules_dict[2], title="Rule 2")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r3(self, ctx):
        """Displays rule 3."""
        await self.simple_embed(ctx, self.rules_dict[3], title="Rule 3")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r4(self, ctx):
        """Displays rule 4."""
        await self.simple_embed(ctx, self.rules_dict[4], title="Rule 4")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r5(self, ctx):
        """Displays rule 5."""
        await self.simple_embed(ctx, self.rules_dict[5], title="Rule 5")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r6(self, ctx):
        """Displays rule 6."""
        await self.simple_embed(ctx, self.rules_dict[6], title="Rule 6")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r7(self, ctx):
        """Displays rule 7."""
        await self.simple_embed(ctx, self.rules_dict[7], title="Rule 7")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r8(self, ctx):
        """Displays rule 8."""
        await self.simple_embed(ctx, self.rules_dict[8], title="Rule 8")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r9(self, ctx):
        """Displays rule 9."""
        await self.simple_embed(ctx, self.rules_dict[9], title="Rule 9")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r10(self, ctx):
        """Displays rule 10."""
        await self.simple_embed(ctx, self.rules_dict[10], title="Rule 10")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def realr11(self, ctx):
        """Displays rule 11."""
        await self.simple_embed(ctx, self.rules_dict[11] + "\n\nIf you simply need to tell someone to not ask about piracy, consider `.pirate` instead. `.r11` was changed to match `.pirate` due to its large embed.", title="Rule 11")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r12(self, ctx):
        """Displays rule 12."""
        await self.simple_embed(ctx, self.rules_dict[12], title="Rule 12")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r13(self, ctx):
        """Displays rule 13."""
        await self.simple_embed(ctx, self.rules_dict[13], title="Rule 13")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r14(self, ctx):
        """Displays rule 14."""
        await self.simple_embed(ctx, self.rules_dict[14], title="Rule 14")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r15(self, ctx):
        """Displays rule 15."""
        await self.simple_embed(ctx, self.rules_dict[15], title="Rule 15")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r16(self, ctx):
        """Displays rule 16."""
        await self.simple_embed(ctx, self.rules_dict[16], title="Rule 16")

    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.channel)
    async def r17(self, ctx):
        """Displays rule 17."""
        await self.simple_embed(ctx, self.rules_dict[17], title="Rule 17")


async def setup(bot):
    await bot.add_cog(Rules(bot))
