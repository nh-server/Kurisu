import discord
import math

from discord.ui import Select
from discord.ext import commands
from itertools import islice
from typing import Union
from utils.context import KurisuContext
from utils.views import BasePaginator, BasePaginatedView

SELECT_MAX_VALUES = 25


class CogHelpPaginator(BasePaginator):
    commands_per_page = 8

    def __init__(self, cog: Union[commands.Cog, commands.Group], commands: list[commands.Command], prefix: str, colour: discord.Colour):
        super().__init__(n_pages=math.ceil(len(commands) / self.commands_per_page))
        self.cog = cog
        self.commands = commands
        self.prefix = prefix
        self.colour = colour

    def current(self) -> discord.Embed:
        if embed := self.pages.get(self.idx):
            return embed
        else:
            index = self.idx * self.commands_per_page
            embed = self.create_embed(commands=self.commands[index:index + self.commands_per_page])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, commands: list[commands.Command]) -> discord.Embed:
        embed = discord.Embed(colour=self.colour)

        embed.title = f"{self.cog.qualified_name} commands"
        embed.description = self.cog.description

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"

        for command in commands:
            # All commands should have a help doc but just in case someone adds one without it.
            embed.add_field(name=f"{command.qualified_name} {command.signature}",
                            value=command.short_doc or "No help for you.", inline=False)

        embed.set_footer(text=f'Use {self.prefix}help [command] for more info about a command.')
        return embed


class MainHelpPaginator(BasePaginator):
    categories_per_page = 9

    def __init__(self, mapping: dict[commands.Cog, list[commands.Command]], description: str, prefix: str, colour: discord.Color):
        super().__init__(n_pages=math.ceil(len(mapping) / self.categories_per_page))
        self.description = description
        self.prefix = prefix
        self.colour = colour
        self.slices = []
        it = iter(mapping)
        # Slice the mapping to mapping 6 cogs each
        for i in range(0, len(mapping), self.categories_per_page):
            self.slices.append({k: mapping[k] for k in islice(it, self.categories_per_page)})

    def current(self) -> discord.Embed:
        if embed := self.pages.get(self.idx):
            return embed
        else:
            embed = self.create_embed(mapping=self.slices[self.idx])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, mapping: dict[commands.Cog, list[commands.Command]]):
        embed = discord.Embed(colour=self.colour)

        embed.title = "Kurisu the bot for Nintendo Homebrew"
        embed.description = f"{self.description}\n\nBelow you will find the categories of commands in Kurisu:"
        embed.set_footer(
            text=f"Use {self.prefix}help [category] for more info about a category or select a category below.")

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"

        for category, cmds in mapping.items():
            if not cmds:
                continue
            embed.add_field(name=f"**{category.qualified_name}** [{len(cmds)}]", value=category.description)

        return embed


class CommandHelpPaginator(BasePaginator):

    def __init__(self, command: commands.Command, prefix: str, colour: discord.Color):
        # Commands have just one page, a paginator is not needed but makes it way easier to integrate with the View
        super().__init__(n_pages=1)
        self.description = command.help or "No help for you."
        self.prefix = prefix
        self.colour = colour
        self.command = command

    def current(self) -> discord.Embed:
        return self.create_embed(command=self.command)

    def create_embed(self, command: commands.Command):
        embed = discord.Embed(title=f"{command.name} command", colour=self.colour)
        embed.description = self.description

        if command.aliases:
            embed.add_field(name="Aliases", value=' '.join(command.aliases), inline=False)

        embed.add_field(name="Usage", value=f"{self.prefix}{command.qualified_name} {command.signature}",
                        inline=False)
        embed.set_footer(text=f"Category: {command.cog_name if command.cog_name else 'No Category'}")
        return embed


class CategorySelect(Select['HelpView']):

    def __init__(self, mapping: dict[commands.Cog, list[commands.Command]], ctx: KurisuContext):
        super().__init__(placeholder="Select a Category.")
        self.ctx = ctx
        self.mapping = mapping
        self.populate()

    def populate(self):
        self.add_option(
            label="Kurisu Categories",
            value="main",
            description="The index of Kurisu Categories.",
            emoji=self.ctx.bot.emoji
        )
        for cog, cmds in self.mapping.items():
            # We don't need commandless cogs here
            if not cmds:
                continue
            emoji = getattr(cog, 'emoji', None)
            self.add_option(label=cog.qualified_name, value=cog.qualified_name, description=cog.description,
                            emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None

        value = self.values[0]

        if value == 'main':
            await self.view.change_paginator(
                MainHelpPaginator(self.mapping, self.ctx.bot.description, self.ctx.clean_prefix, colour=self.ctx.bot.colour), interaction)
        else:
            cog = self.ctx.bot.get_cog(value)

            if cog is None:
                await interaction.response.send_message("Error when fetching cog.", ephemeral=True)
                return

            commands = self.mapping[cog]
            await self.view.change_paginator(CogHelpPaginator(cog, commands, self.ctx.clean_prefix, self.ctx.bot.colour), interaction)


class CommandSelect(Select['HelpView']):

    def __init__(self, cog: Union[commands.Cog, commands.Group], commands: list[commands.Command],
                 ctx: KurisuContext, suffix: str = ""):
        super().__init__(placeholder="Select a command" + suffix)
        self.ctx = ctx
        self.cog = cog
        self.commands = commands
        self.populate()

    def populate(self):
        self.add_option(
            label=f"{self.cog.qualified_name} commands",
            value="main",
            description=f"{self.cog.qualified_name} commands.",
            emoji=self.ctx.bot.emoji
        )

        for command in self.commands:
            self.add_option(label=command.name, value=command.qualified_name, description=command.description)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None

        value = self.values[0]

        if value == 'main':
            await self.view.change_paginator(CogHelpPaginator(self.cog, self.commands, self.ctx.clean_prefix, self.ctx.bot.colour),
                                             interaction)
        else:
            command = self.ctx.bot.get_command(value)
            if command is None:
                await interaction.response.send_message("Error when fetching command.", ephemeral=True)
                return
            await self.view.change_paginator(CommandHelpPaginator(command, self.ctx.clean_prefix, self.ctx.bot.colour), interaction)


class HelpView(BasePaginatedView):

    async def change_paginator(self, paginator: Union[MainHelpPaginator, CogHelpPaginator, CommandHelpPaginator],
                               interaction: discord.Interaction):
        self.paginator = paginator

        if self.paginator.n_pages > 1:
            self.reset_buttons()
        else:
            self.disable_buttons()

        await interaction.response.edit_message(embed=self.paginator.current(), view=self)


class KuriHelp(commands.HelpCommand):
    context: KurisuContext

    def __init__(self):
        super().__init__(show_hidden=True, context=KurisuContext)

    async def prepare_help_command(self, ctx, command=None):
        await ctx.bot.wait_until_all_ready()

    async def send_bot_help(self, mapping: dict[commands.Cog, list[commands.Command]]):
        f_mapping = {}
        # Create a mapping with the commands filtered
        for cog, cmds in mapping.items():
            if cog and (f_cmds := await self.filter_commands(cmds, sort=True)):
                f_mapping[cog] = f_cmds

        bot = self.context.bot
        colour = self.context.bot.colour

        view = HelpView(MainHelpPaginator(f_mapping, bot.description, self.context.prefix, colour), self.context.author)
        view.add_item(CategorySelect(f_mapping, self.context))

        channel = self.get_destination()
        msg = await channel.send(embed=view.paginator.current(), view=view, reference=self.context.message)
        view.message = msg

    async def send_cog_help(self, cog: commands.Cog):
        commands = await self.filter_commands(cog.get_commands(), sort=True)

        view = HelpView(CogHelpPaginator(cog, commands, self.context.prefix, self.context.bot.colour), self.context.author)

        # All my homies hate Assistance
        # If there is >25 commands create multiple Selects and add a suffix indicating what commands are inside [A-C]
        if len(commands) > SELECT_MAX_VALUES:
            for i in range(0, len(commands), SELECT_MAX_VALUES - 1):
                view.add_item(CommandSelect(cog, commands[i:i + SELECT_MAX_VALUES - 1], self.context,
                                            suffix=f"[{commands[i].name[0].upper()}-{commands[i:i + SELECT_MAX_VALUES - 2][-1].name[0].upper()}]"))
        else:
            view.add_item(CommandSelect(cog, commands, self.context))

        channel = self.get_destination()
        msg = await channel.send(embed=view.paginator.current(), view=view, reference=self.context.message)
        view.message = msg

    async def send_group_help(self, group: commands.Group):
        commands = await self.filter_commands(group.commands, sort=True)

        view = HelpView(CogHelpPaginator(group, commands, self.context.clean_prefix, self.context.bot.colour), self.context.author)
        view.add_item(CommandSelect(group.cog, commands, self.context))

        channel = self.get_destination()
        msg = await channel.send(embed=view.paginator.current(), view=view, reference=self.context.message)
        view.message = msg

    async def send_command_help(self, command: commands.Command):
        embed = CommandHelpPaginator(command, self.context.clean_prefix, self.context.bot.colour).current()
        channel = self.get_destination()
        await channel.send(embed=embed, reference=self.context.message)

    async def send_error_message(self, error: str):
        embed = discord.Embed(title="Not Found", description=error, colour=self.context.bot.colour)
        channel = self.get_destination()
        await channel.send(embed=embed)
