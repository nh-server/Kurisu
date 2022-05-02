import discord

from discord.ui import Select
from discord.ext import commands

SELECT_MAX_VALUES = 25


class CategorySelect(Select['HelpView']):

    def __init__(self, options: list[discord.SelectOption], placeholder: str, mapping):
        super().__init__(options=options, placeholder=placeholder)
        self.mapping = mapping

    async def callback(self, interaction: discord.MessageInteraction):
        await interaction.response.defer()
        value = self.values[0]
        if value in self.view.embed_cache:
            embed = self.view.embed_cache[value]
        else:
            cog = discord.utils.get(self.mapping, qualified_name=value)
            embed = await self.view.help.create_category_embed(cog)
            self.view.embed_cache[value] = embed
        await interaction.message.edit(embed=embed)


class CommandSelect(discord.ui.Select['HelpView']):

    def __init__(self, options: list[discord.SelectOption], placeholder: str, commands):
        super().__init__(options=options, placeholder=placeholder)
        self.commands = commands

    async def callback(self, interaction: discord.MessageInteraction):
        await interaction.response.defer()
        value = self.values[0]
        if value in self.view.embed_cache:
            embed = self.view.embed_cache[value]
        else:
            command = discord.utils.get(self.commands, name=value)
            if isinstance(command, commands.Group):
                embed = await self.view.help.create_group_embed(command)
                embed.set_footer(text=f"Use {self.view.help.context.clean_prefix}help {command.name} for more info about a subcommand")
            else:
                embed = await self.view.help.create_command_embed(command)
            self.view.embed_cache[value] = embed
        await interaction.message.edit(embed=embed)


class HelpView(discord.ui.View):

    def __init__(self, help):
        super().__init__(timeout=30)
        self.help = help
        self.embed_cache: dict[str, discord.Embed] = {}
        self.message = None

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)
        self.stop()


class KuriHelp(commands.HelpCommand):

    async def create_category_embed(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(title=f"{cog.qualified_name} commands", colour=self.context.bot.colour)
        embed.description = f"{cog.description}"
        embed.set_footer(text=f"Use {self.context.clean_prefix}help [command] for more info about a command or select a category below.")
        commands = await self.filter_commands(cog.get_commands())
        if len(commands) < 20:
            cmds = "\n\n".join(f"{cmd.name} - {cmd.help}" for cmd in commands)
        else:
            cmds = " ".join(f"{cmd.name}" for cmd in commands)
        embed.add_field(name="Commands", value=cmds)
        return embed

    async def create_command_embed(self, command: commands.Command) -> discord.Embed:
        embed = discord.Embed(title=f"{command} command", colour=self.context.bot.colour)
        embed.description = command.help
        if command.aliases:
            embed.add_field(name="Aliases", value=' '.join(command.aliases), inline=False)
        embed.add_field(name="Usage", value=self.get_command_signature(command), inline=False)
        return embed

    async def create_group_embed(self, group: commands.Group) -> discord.Embed:
        embed = discord.Embed(title=f"{group} group", colour=self.context.bot.colour)
        embed.description = group.help
        for cmd in await self.filter_commands(group.commands):
            embed.add_field(name=cmd.name, value=cmd.help)
        return embed

    async def create_select_options(self, commands, default: str) -> list[discord.SelectOption]:
        options = [discord.SelectOption(label=default)]
        for command in await self.filter_commands(commands):
            options.append(discord.SelectOption(label=command.name))
        return options

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help is here!", colour=0xb01ec3)
        embed.description = f"{self.context.bot.description}"
        embed.set_footer(text=f"Use {self.context.clean_prefix}help [category] for more info about a category or select a category below.")
        f_mapping = {}
        options = [discord.SelectOption(label="Bot Help", emoji=self.context.bot.emoji)]
        for category, cmds in mapping.items():
            if category and (f_cmds := await self.filter_commands(cmds)):
                f_mapping[category] = f_cmds
                options.append(discord.SelectOption(label=category.qualified_name, emoji=getattr(category, 'emoji', None)))
                embed.add_field(name=f"**{category.qualified_name}** [{len(f_cmds)}]", value=category.description)

        view = HelpView(self)
        view.embed_cache['Bot Help'] = embed
        view.add_item(CategorySelect(options=options, placeholder='Select a category', mapping=f_mapping))

        channel = self.get_destination()
        msg = await channel.send(embed=embed, view=view, reference=self.context.message)
        view.message = msg

    async def send_cog_help(self, cog: commands.Cog):
        embed = await self.create_category_embed(cog)
        commands = await self.filter_commands(cog.get_commands(), sort=True)

        view = HelpView(self)
        view.embed_cache['Category'] = embed
        options = await self.create_select_options(commands, "Category")
        # All my homies hate Assistance
        if len(options) > SELECT_MAX_VALUES:
            for i in range(0, len(options), SELECT_MAX_VALUES):
                view.add_item(CommandSelect(options=options[i:i + SELECT_MAX_VALUES], placeholder=f'Select a command [{commands[i].name[0]}-{commands[i:i + SELECT_MAX_VALUES-1][-1].name[0]}]', commands=cog.get_commands()))
        else:
            view.add_item(CommandSelect(options=options, placeholder='Select a command', commands=cog.get_commands()))

        channel = self.get_destination()
        msg = await channel.send(embed=embed, view=view, reference=self.context.message)
        view.message = msg

    async def send_group_help(self, group: commands.Group):
        embed = await self.create_group_embed(group)
        embed.set_footer(text=f"Use {self.context.clean_prefix}help {group.name} [command] for more info about a subcommand or select a subcommand below.")

        view = HelpView(self)
        options = await self.create_select_options(group.commands, "Group")
        view.add_item(CommandSelect(options=options, placeholder='Select a subcommand', commands=group.commands))
        view.embed_cache['Group'] = embed

        channel = self.get_destination()
        msg = await channel.send(embed=embed, view=view, reference=self.context.message)
        view.message = msg

    async def send_command_help(self, command: commands.Command):
        embed = await self.create_command_embed(command)
        channel = self.get_destination()
        await channel.send(embed=embed, reference=self.context.message)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Not Found", description=error, colour=self.context.bot.colour)
        channel = self.get_destination()
        await channel.send(embed=embed)
