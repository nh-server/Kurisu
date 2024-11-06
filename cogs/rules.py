from __future__ import annotations

import discord
import json

from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import is_staff
from utils.database.configuration import Rule
from utils.utils import paginate_message, KurisuCooldown, text_to_discord_file, simple_embed, gen_color
from utils.views import BasePaginator, PaginatedEmbedView


if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext


class RulePaginator(BasePaginator):

    def __init__(self, rules: dict[int, Rule]):
        super().__init__(n_pages=len(rules))
        self.rules = rules

    def current(self):
        if embed := self.pages.get(self.idx):
            return embed
        else:
            embed = self.create_embed(self.rules[self.idx + 1])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, rule: Rule):
        return discord.Embed(title=f"Rule {self.idx + 1} - {rule.title}", description=rule.description, colour=0x128bed)


def create_rule_cmd(rule: Rule):
    async def rule_cmd(self, ctx: commands.Context):
        await simple_embed(ctx, rule.description,
                           title=f"Rule {rule.number} - {rule.title}", color=gen_color(rule.number))

    cmd = rule_cmd
    cmd.__name__ = f"r{rule.number}"
    cmd.__qualname__ = f"{Rules.qualified_name}.{cmd.__name__}"

    cmd.__doc__ = f"Displays rule {rule.number}."

    # this feels _wrong_ but is probably the best way to do this
    cooldown = commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)(
        cmd)
    cmd_obj = commands.command(name=cmd.__name__)(cooldown)
    return cmd_obj


class Rules(commands.Cog):
    """
    Read da rules.
    """
    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot
        self.emoji = discord.PartialEmoji.from_str('📖')
        self.configuration = self.bot.configuration

    async def cog_load(self):
        self.bg_task = self.bot.loop.create_task(self.init_rules())

    async def init_rules(self):
        await self.bot.wait_until_all_ready()
        self.nh_emoji = discord.utils.get(self.bot.guild.emojis, name="nintendo_homebrew") or "⁉"
        self.logo_3ds = discord.utils.get(self.bot.guild.emojis, name="3dslogo") or "⁉"
        self.logo_wiiu = discord.utils.get(self.bot.guild.emojis, name="wiiulogo") or "⁉"
        self.logo_switch = discord.utils.get(self.bot.guild.emojis, name="switchlogo") or "⁉"

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
Usernames must begin with at least one alphanumeric character and are to be primarily alphanumeric, to keep them easy to tag and read.
Excessively long usernames are not acceptable. Usernames and avatars that are annoying, offensive, inappropriate ("nsfw"), and/or disruptive to others are also not allowed.
Usernames that go against these rules will be assigned a nickname. Users are able to change their own nickname, but may be blocked from messaging by AutoMod if the selected nickname or profile name is not acceptable.
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

        self.extra = f"""While we appreciate everyone who boosts the server **IT DOES NOT MAKE YOU EXEMPT FROM THE RULES.** We've given boosters reaction perms in {self.bot.channels['off-topic'].mention}, {self.bot.channels['elsewhere'].mention}, and {self.bot.channels['nintendo-discussion'].mention}, and you can also stream in the Streaming gamer voice channel.
📨 Invitation link This is a permanent invitation link to the server!
https://discord.gg/C29hYvh"""

    @is_staff('SuperOP')
    @commands.command()
    async def updaterules(self, ctx: KurisuContext):
        """Updates the rules in Welcome and Rules"""
        channel = self.bot.channels['welcome-and-rules']
        async for message in channel.history():
            await message.delete()
        await channel.send(self.rules_intro)
        for number, rule in sorted(self.configuration.rules.items()):
            await channel.send(f"**{number}**. {rule}\n")
        await channel.send(self.staff_action)
        staff = [f"<@{staff}>" for staff in self.configuration.staff]
        await channel.send(self.mod_list + '\n'.join(staff))
        helpers = self.configuration.helpers
        helpers_3ds = [f"<@{helper}>" for helper, console in helpers.items() if console == '3DS']
        helpers_wiiu = [f"<@{helper}>" for helper, console in helpers.items() if console == 'WiiU']
        helpers_legacy = [f"<@{helper}>" for helper, console in helpers.items() if console == 'Legacy']
        helpers_switch = [f"<@{helper}>" for helper, console in helpers.items() if console == 'Switch']
        helpers_wii = [f"<@{helper}>" for helper, console in helpers.items() if console == 'Wii']
        await channel.send(self.helper_list)
        await channel.send(f"{str(self.logo_3ds)}  Nintendo 3DS\n" + '\n'.join(helpers_3ds))
        await channel.send(f"{str(self.logo_wiiu)}  Wii U\n" + '\n'.join(helpers_wiiu))
        await channel.send(f"{str(self.logo_switch)}  Nintendo Switch\n" + '\n'.join(helpers_switch))
        await channel.send("Nintendo Wii\n" + '\n'.join(helpers_wii))
        await channel.send("Legacy\n" + '\n'.join(helpers_legacy))
        await channel.send(self.nickname_policy)
        await channel.send(self.useful_commands)
        await channel.send(self.extra)
        await ctx.send("Updated rules successfully!")

    @is_staff('SuperOP')
    @commands.group()
    async def rule(self, ctx: KurisuContext):
        """Group to manage the server rules."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @rule.command(name='add')
    async def add_rule(self, ctx: KurisuContext, number: int, title: str, description: str):
        """Adds or edits a current rule"""
        if self.configuration.rules.get(number):
            await self.configuration.edit_rule(number, title, description)
            await ctx.send(f"Rule {number} edited successfully!")
        else:
            await self.configuration.add_rule(number, title, description)
            await ctx.send(f"Rule {number} added successfully!")

    @rule.command(name='delete')
    async def delete_rule(self, ctx: KurisuContext, number: int):
        if self.configuration.rules.get(number):
            await self.configuration.delete_rule(number)
            await ctx.send(f"Rule {number} deleted successfully!")
        else:
            await ctx.send(f"There is no rule {number}!")

    @rule.command(name='list')
    async def list_rules(self, ctx: KurisuContext):
        if self.configuration.rules:
            rules = [f"**{number}**. {rule}\n" for number, rule in self.configuration.rules.items()]
            for page in paginate_message("".join(rules), suffix='', prefix='').pages:
                await ctx.send(page)
        else:
            await ctx.send("There are no rules!")

    @commands.command()
    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    async def consoleban(self, ctx: KurisuContext):
        """States some stuff about no assistance with bans"""
        await ctx.send("Please refrain from asking for or giving assistance with"
                       " unbanning consoles which have been banned from online services.\n"
                       "Reminder: sharing files that allow other users to evade "
                       "Nintendo issued bans is a bannable offense.")

    @commands.command(aliases=['r11'])
    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    async def pirate(self, ctx: KurisuContext):
        """Hey! You can't steal another trainer's Pokémon!"""
        await ctx.send("Please refrain from asking for or giving assistance with installing, using, or obtaining pirated software.")

    @commands.command()
    @commands.dynamic_cooldown(KurisuCooldown(1, 30.0), commands.BucketType.channel)
    async def nick(self, ctx: KurisuContext):
        """Displays the Nickname and Avatar Policy."""
        await ctx.send(self.nickname_policy)

    @commands.command()
    async def rules(self, ctx: KurisuContext):
        """Links to the welcome-and-rules channel."""
        view = PaginatedEmbedView(paginator=RulePaginator(self.configuration.rules), author=ctx.author)
        msg = await ctx.send(embed=view.paginator.current(), view=view)
        view.message = msg

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command()
    async def rules_dump(self, ctx: KurisuContext):
        msg = {}
        for number, rule in sorted(self.configuration.rules.items()):
            print(number)
            print(type(number))
            msg[number] = {'title': rule.title, 'description': rule.description}
        file = text_to_discord_file(json.dumps(msg, sort_keys=True), name="rules.json")
        await ctx.send(file=file)

    @is_staff("Owner")
    @commands.guild_only()
    @commands.command()
    async def rules_load(self, ctx: KurisuContext, file: discord.Attachment):
        try:
            text = (await file.read()).decode('utf-8')
            rules: dict[str, dict[str, str]] = json.loads(text)
        except UnicodeDecodeError:
            return await ctx.send("Invalid file.")
        await self.configuration.wipe_rules()
        for rule_number, content in rules.items():
            await self.configuration.add_rule(int(rule_number), content['title'], content['description'])
        await ctx.send("Rules loaded!")


async def setup(bot):
    for rule in bot.configuration.rules.values():
        cmd = create_rule_cmd(rule)
        setattr(Rules, f"r{rule.number}", cmd)
        Rules.__cog_commands__.append(cmd)
    await bot.add_cog(Rules(bot))
