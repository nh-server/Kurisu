import datetime
import discord
import io
import random
import re
import traceback

from discord.ext import commands
from discord.utils import format_dt
from utils import crud, checks
from typing import Optional, Union


class ConsoleColor(discord.Color):

    @classmethod
    def n3ds(cls):
        return cls(0xCE181E)

    @classmethod
    def wiiu(cls):
        return cls(0x009AC7)

    @classmethod
    def switch(cls):
        return cls(0xE60012)

    @classmethod
    def wii(cls):
        return cls(0x009AC7)

    @classmethod
    def legacy(cls):
        return cls(0x707070)


async def send_dm_message(member: discord.Member, message: str, ctx: commands.Context = None, **kwargs) -> bool:
    """A helper method for sending a message to a member's DMs.

    Returns a boolean indicating success of the DM
    and notifies of the failure if ctx is supplied."""
    try:
        await member.send(message, **kwargs)
        return True
    except (discord.HTTPException, discord.Forbidden, discord.NotFound, AttributeError):
        if ctx:
            await ctx.send(f"Failed to send DM message to {member.mention}")
        return False


async def get_user(ctx: Union[commands.Context, discord.Interaction], user_id: int) -> Optional[Union[discord.Member, discord.User]]:
    if ctx.guild and (user := ctx.guild.get_member(user_id)):
        return user
    else:
        bot = ctx.bot if isinstance(ctx, commands.Context) else ctx.client
        return await bot.fetch_user(user_id)


def command_signature(command, *, prefix=".") -> str:
    """Helper method for a command signature

    Parameters
    -----------
    command: :class:`discord.ext.commands.Command`
        The command to generate a signature for
    prefix: str
        The prefix to include in the signature"""
    return f"{discord.utils.escape_markdown(prefix)}{command.qualified_name} {command.signature}"


def gen_color(seed) -> discord.Color:
    random.seed(seed)
    c_r = random.randint(0, 255)
    c_g = random.randint(0, 255)
    c_b = random.randint(0, 255)
    return discord.Color((c_r << 16) + (c_g << 8) + c_b)


def parse_time(time_string) -> int:
    """Parses a time string in dhms format to seconds"""
    # thanks Luc#5653
    units = {
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1
    }
    match = re.findall("([0-9]+[smhd])", time_string)  # Thanks to 3dshax server's former bot
    if not match:
        return -1
    return sum(int(item[:-1]) * units[item[-1]] for item in match)


def parse_date(date_string) -> int:
    date_lst: list = date_string.split(' ')
    now = datetime.datetime.utcnow()

    if len(date_lst) == 1:
        date_lst.append('00:00')
    elif len(date_lst) != 2:
        return -1

    try:
        datetime_obj = datetime.datetime.strptime(' '.join(date_lst), "%Y-%m-%d %H:%M")
    except ValueError:
        return -1
    delta = datetime_obj - now
    return int(delta.total_seconds())


class DateOrTimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, arg: str):
        if (seconds := parse_date(arg)) != -1:
            return seconds
        elif (seconds := parse_time(arg)) != -1:
            return seconds
        raise commands.BadArgument("Invalid date/time format")


def time_converter(inter, time_string: str) -> int:
    return parse_time(time_string)


def create_error_embed(ctx: Union[commands.Context, discord.CommandInteraction], exc: commands.CommandError) -> discord.Embed:
    interaction = isinstance(ctx, discord.ApplicationCommandInteraction)
    command: str = ctx.application_command.name if interaction else str(ctx.command)
    embed = discord.Embed(title=f"Unexpected exception in command {command}", color=0xe50730)
    trace = "".join(traceback.format_exception(etype=None, value=exc, tb=exc.__traceback__))
    if len(trace) > 4080:
        trace = trace[-4080:]
    embed.description = f'```py\n{trace}```'
    embed.add_field(name="Exception Type", value=exc.__class__.__name__)
    embed.add_field(name="Information", value=f"channel: {ctx.channel.mention if isinstance(ctx.channel, discord.TextChannel) else 'Direct Message'}\ncommand: {command}\nauthor: {ctx.author.mention}\n{f'message: {ctx.message.content}' if not interaction else ''}", inline=False)
    return embed


def paginate_message(msg: str, prefix: str = '```', suffix: str = '```', max_size: int = 2000):
    paginator = commands.Paginator(prefix=prefix, suffix=suffix, max_size=max_size)
    sep = max_size - len(prefix) - len(suffix) - 2
    for chunk in [msg[i:i + sep] for i in range(0, len(msg), sep)]:
        paginator.add_line(chunk)
    return paginator


def text_to_discord_file(text: str, *, name: str = 'output.txt'):
    encoded = text.encode("utf-8")
    return discord.File(filename=name, fp=io.BytesIO(encoded))


class BasePaginator:
    """Serves as base class for paginators for a BasePaginatedView, not to be used as-is"""
    def __init__(self, n_pages):
        self.n_pages = n_pages
        self.idx = 0
        self.pages: dict[int, discord.Embed] = {}

    def previous(self):
        self.idx = max(self.idx - 1, 0)

    def next(self):
        self.idx = min(self.idx + 1, self.n_pages - 1)

    def first(self):
        self.idx = 0

    def last(self):
        self.idx = self.n_pages - 1

    def is_first(self):
        return self.idx == 0

    def is_last(self):
        return self.idx == self.n_pages - 1

    def current(self):
        raise NotImplementedError


class BasePaginatedView(discord.ui.View):
    """Base class for a paginated view using a BasePaginator subclass"""

    def __init__(self, paginator: BasePaginator, author: Optional[Union[discord.Member, discord.User]], timeout: int = 30):
        super().__init__(timeout=timeout)
        self.paginator = paginator
        self.message = None
        self.author = author

        if self.paginator.n_pages == 1:
            self.disable_buttons()

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.MessageInteraction) -> bool:
        if self.author and interaction.user.id != self.author.id:
            await interaction.response.send_message("This view is not for you.", ephemeral=True)
            return False
        return True

    def reset_buttons(self):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False

    def disable_buttons(self):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = True
        self.last_page.disabled = True

    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary, disabled=True)
    async def first_page(self, button: discord.ui.Button, interaction: discord.MessageInteraction):
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        self.paginator.first()
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.primary, disabled=True)
    async def prev_page(self, button: discord.ui.Button, interaction: discord.MessageInteraction):
        self.next_page.disabled = False
        self.last_page.disabled = False
        self.paginator.previous()
        if self.paginator.is_first():
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
    async def next_page(self, button: discord.ui.Button, interaction: discord.MessageInteraction):
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.paginator.next()
        if self.paginator.is_last():
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary)
    async def last_page(self, button: discord.ui.Button, interaction: discord.MessageInteraction):
        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        self.paginator.last()
        await interaction.response.edit_message(embed=self.paginator.current(), view=self)

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.red)
    async def remove(self, button: discord.ui.Button, interaction: discord.MessageInteraction):
        await interaction.response.edit_message(view=None)
        self.stop()


class PaginatedEmbedView(BasePaginatedView):
    def __init__(self, paginator: BasePaginator, timeout: int = 20, author: discord.Member = None):
        super().__init__(paginator=paginator, timeout=timeout, author=author)
        if self.paginator.n_pages == 1:
            self.clear_items()


class VoteButton(discord.ui.Button):
    def __init__(self, custom_id: str, label: str, style: discord.ButtonStyle = discord.ButtonStyle.secondary):
        super().__init__(style=style, label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.MessageInteraction):
        if self.view.staff_only and not await checks.check_staff_id('Helper', interaction.user.id):
            await interaction.response.send_message("You aren't allowed to vote.", ephemeral=True)
            return
        await crud.add_voteview_vote(self.view.custom_id, interaction.user.id, self.label)
        await interaction.response.send_message("Vote added.", ephemeral=True)


class VoteButtonEnd(discord.ui.Button['SimpleVoteView']):
    def __init__(self, custom_id: str, style: discord.ButtonStyle = discord.ButtonStyle.red):
        super().__init__(style=style, label='End', custom_id=custom_id)

    async def callback(self, interaction: discord.MessageInteraction):
        if interaction.user.id == self.view.author_id:
            # Try to remove the view
            if self.view.message_id:
                msg = await interaction.channel.fetch_message(self.view.message_id)
                await msg.edit(view=None)

            await self.view.calculate_votes()
            results = "results:\n" + '\n'.join(f"{op}: {count}" for op, count in self.view.count.items())
            await interaction.response.send_message(
                f"Vote started {format_dt(self.view.start, style='R')} has finished.\n{results}")
            self.view.stop()
            await crud.remove_vote_view(self.view.custom_id)
        else:
            await interaction.response.send_message("Only the vote creator can end it", ephemeral=True)


class SimpleVoteView(discord.ui.View):
    def __init__(self, author_id: int, options: list[str], custom_id: int, start: datetime.datetime, staff_only: bool = False):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.custom_id = custom_id
        self.message_id = None
        self.start = start
        self.staff_only = staff_only
        self.count: dict[str, int] = {}
        for n, option in enumerate(options):
            self.count[option] = 0
            self.add_item(VoteButton(label=option, custom_id=f"{custom_id}_{n}"))
        self.add_item(VoteButtonEnd(custom_id=f"{custom_id}_{len(self.children)+1}"))

    async def calculate_votes(self):
        for vote in await crud.get_voteview_votes(self.custom_id):
            self.count[vote.option] = self.count[vote.option] + 1
