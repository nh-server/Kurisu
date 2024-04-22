import discord
import math

from discord import Interaction
from discord.app_commands import AppCommandGroup, AppCommand
from discord.ui import Select
from discord.ext.commands import Cog, Group, Command, HelpCommand
from itertools import islice, batched
from utils.context import KurisuContext
from utils.views import BasePaginator, BasePaginatedView

SELECT_MAX_VALUES = 25


class CategoryHelpPaginator(BasePaginator):
    commands_per_page = 8

    def __init__(self, category: Cog | Group | AppCommand, commands: list[Command] | list[AppCommandGroup],
                 ctx: KurisuContext):
        super().__init__(n_pages=math.ceil(len(commands) / self.commands_per_page))
        self.category = category
        self.commands = commands
        self.ctx = ctx

    def current(self) -> discord.Embed:
        if embed := self.pages.get(self.idx):
            return embed
        else:
            index = self.idx * self.commands_per_page
            embed = self.create_embed(commands=self.commands[index:index + self.commands_per_page])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, commands: list[Command] | list[AppCommandGroup]) -> discord.Embed:
        embed = discord.Embed(colour=self.ctx.bot.colour)

        if not self.ctx.interaction:
            assert isinstance(self.category, (Cog, Group))
            embed.title = f"{self.category.qualified_name} commands"
            embed.description = self.category.help if isinstance(self.category, Group) else self.category.description

            for command in commands:
                assert isinstance(command, Command)
                # All commands should have a help doc but just in case someone adds one without it.
                embed.add_field(name=f"{command.qualified_name} {command.signature}",
                                value=command.short_doc or "No help for you.", inline=False)
            embed.set_footer(text=f'Use {self.ctx.clean_prefix}help [command] for more info about a command.')
        else:
            assert isinstance(self.category, AppCommand)
            embed.title = f"{self.category.name} slash commands"
            embed.description = self.category.description
            embed.add_field(name="Commands",
                            value='\n'.join(f"{c.mention}: {c.description}" for c in commands))  # type: ignore
        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"
        return embed


class MainHelpPaginator(BasePaginator):
    categories_per_page = 9

    def __init__(self, mapping: dict[Cog, list[Command]] | dict[AppCommand, list[AppCommandGroup]],
                 ctx: 'KurisuContext'):
        super().__init__(n_pages=math.ceil(len(mapping) / self.categories_per_page))
        self.ctx = ctx
        self.slices = []
        it = iter(mapping)
        # Slice the mapping to mapping 6 cogs each
        for i in range(0, len(mapping), self.categories_per_page):
            self.slices.append({k: mapping[k] for k in islice(it, self.categories_per_page)})  # type: ignore

    def current(self) -> discord.Embed:
        if embed := self.pages.get(self.idx):
            return embed
        else:
            embed = self.create_embed(mapping=self.slices[self.idx])
            self.pages[self.idx] = embed
            return embed

    def create_embed(self, mapping: dict[Cog, list[Command]] | dict[AppCommand, list[AppCommandGroup]]):
        embed = discord.Embed(colour=self.ctx.bot.colour)

        embed.title = "Kurisu the bot for Nintendo Homebrew"
        embed.description = f"{self.ctx.bot.description}\n\nBelow you will find the categories of commands in Kurisu:"
        if not self.ctx.interaction:
            embed.set_footer(
                text=f"Use {self.ctx.clean_prefix}help [category] for more info about a category or select a category below.")

        if self.n_pages > 1:
            embed.title += f" [{self.idx + 1}/{self.n_pages}]"

        for category, cmds in mapping.items():
            if not cmds:
                continue
            embed.add_field(
                name=f"**{category.qualified_name if not self.ctx.interaction else category.name}** [{len(cmds)}]",  # type: ignore
                value=category.description)

        return embed


class CommandHelpPaginator(BasePaginator):

    def __init__(self, command: Command, prefix: str, colour: discord.Color):
        # Commands have just one page, a paginator is not needed but makes it way easier to integrate with the View
        super().__init__(n_pages=1)
        self.description = command.help or "No help for you."
        self.prefix = prefix
        self.colour = colour
        self.command = command

    def current(self) -> discord.Embed:
        return self.create_embed(command=self.command)

    def create_embed(self, command: Command):
        embed = discord.Embed(title=f"{command.name} command", colour=self.colour)
        embed.description = self.description

        if command.aliases:
            embed.add_field(name="Aliases", value=' '.join(command.aliases), inline=False)

        embed.add_field(name="Usage", value=f"{self.prefix}{command.qualified_name} {command.signature}",
                        inline=False)

        if examples := command.extras.get('examples'):
            embed.add_field(name="Examples", value='\n'.join(examples))

        embed.set_footer(text=f"Category: {command.cog_name if command.cog_name else 'No Category'}")
        return embed


class CategorySelect(Select['HelpView']):

    def __init__(self, mapping: dict[Cog, list[Command]] | dict[AppCommand, list[AppCommandGroup]], ctx: KurisuContext,
                 *, placeholder: str = "Select a Category", index_label: str = "Kurisu Categories",
                 index_description: str = "The index of Kurisu Categories."):
        super().__init__(placeholder=placeholder)
        self.mapping = mapping
        self.ctx = ctx
        self.index_label = index_label
        self.index_description = index_description
        self.populate()

    def populate(self):
        self.add_option(
            label=self.index_label,
            value="main",
            description=self.index_description,
            emoji=self.ctx.bot.emoji
        )
        for category, cmds in self.mapping.items():
            # We don't need commandless categories here
            if not cmds:
                continue
            emoji = getattr(category, 'emoji', None)
            name = category.name if self.ctx.interaction else category.qualified_name  # type: ignore
            self.add_option(label=f"{name} [{len(cmds)}]",
                            value=name,
                            description=category.description,
                            emoji=emoji)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        value = self.values[0]

        if value == 'main':
            await self.view.change_paginator(
                MainHelpPaginator(self.mapping, self.view.ctx), interaction)
        else:
            if self.view.ctx.interaction:
                category = discord.utils.get(self.mapping, name=value)
            else:
                category = self.view.ctx.bot.get_cog(value)

            if category is None:
                await interaction.response.send_message("Error when fetching category.", ephemeral=True)
                return

            commands = self.mapping[category]  # type: ignore
            await self.view.change_paginator(CategoryHelpPaginator(category, commands, self.view.ctx), interaction)


class CommandSelect(Select['HelpView']):

    def __init__(self, cog: Cog | Group, commands: list[Command],
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

    async def callback(self, interaction: Interaction):
        assert self.view is not None

        value = self.values[0]

        if value == 'main':
            await self.view.change_paginator(CategoryHelpPaginator(self.cog, self.commands, self.ctx),
                                             interaction)
        else:
            command = self.ctx.bot.get_command(value)
            if command is None:
                await interaction.response.send_message("Error when fetching command.", ephemeral=True)
                return
            await self.view.change_paginator(CommandHelpPaginator(command, self.ctx.prefix, self.view.ctx.bot.colour),
                                             interaction)


class HelpView(BasePaginatedView):

    def __init__(self, paginator: BasePaginator, ctx: KurisuContext):
        super().__init__(paginator, ctx.author)
        self.author: discord.Member
        self.ctx = ctx

    async def change_paginator(self, paginator: MainHelpPaginator | CategoryHelpPaginator | CommandHelpPaginator,
                               interaction: Interaction):
        self.paginator = paginator

        if self.paginator.n_pages > 1:
            self.reset_buttons()
        else:
            self.disable_buttons()

        await interaction.response.edit_message(embed=self.paginator.current(), view=self)


class KuriHelp(HelpCommand):
    context: KurisuContext

    def __init__(self):
        super().__init__(show_hidden=True, context=KurisuContext)

    async def prepare_help_command(self, ctx, command=None):
        await ctx.bot.wait_until_all_ready()

    async def send_bot_help(self, mapping: dict[Cog, list[Command]]):
        f_mapping = {}
        # Create a mapping with the commands filtered
        for cog, cmds in mapping.items():
            if cog and (f_cmds := await self.filter_commands(cmds, sort=True)):
                f_mapping[cog] = f_cmds

        view = HelpView(MainHelpPaginator(f_mapping, self.context), self.context)

        if len(f_mapping) > SELECT_MAX_VALUES - 1:
            for n, batch_map in enumerate(batched(f_mapping.items(), SELECT_MAX_VALUES - 1)):
                view.add_item(CategorySelect(dict(batch_map),
                                             self.context,
                                             placeholder=f"Select a category [{1+(SELECT_MAX_VALUES - 1)*n}-{1+(SELECT_MAX_VALUES - 1)*n+len(batch_map)}]",
                                             index_label=f"Kurisu Categories Part {n+1}",
                                             index_description=f"Index of Part {n+1}"))
        else:
            view.add_item(CategorySelect(f_mapping, self.context))

        channel = self.get_destination()
        msg = await channel.send(embed=view.paginator.current(), view=view, reference=self.context.message)
        view.message = msg

    async def send_cog_help(self, cog: Cog):
        commands = await self.filter_commands(cog.get_commands(), sort=True)

        view = HelpView(CategoryHelpPaginator(cog, commands, self.context), self.context)

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

    async def send_group_help(self, group: Group):
        commands = await self.filter_commands(group.commands, sort=True)

        view = HelpView(CategoryHelpPaginator(group, commands, self.context), self.context)
        view.add_item(CommandSelect(group.cog, commands, self.context))

        channel = self.get_destination()
        msg = await channel.send(embed=view.paginator.current(), view=view, reference=self.context.message)
        view.message = msg

    async def send_command_help(self, command: Command):
        embed = CommandHelpPaginator(command, self.context.clean_prefix, self.context.bot.colour).current()
        channel = self.get_destination()
        await channel.send(embed=embed, reference=self.context.message)

    async def send_error_message(self, error: str):
        embed = discord.Embed(title="Not Found", description=error, colour=self.context.bot.colour)
        channel = self.get_destination()
        await channel.send(embed=embed)
