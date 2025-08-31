import discord
import random

from discord.ext.commands import Cog, Group, Command, HelpCommand
from itertools import batched
from utils.context import KurisuContext
from utils.views.help import CategoryHelpPaginator, MainHelpPaginator, CommandHelpPaginator, CategorySelect, \
    CommandSelect, HelpView

SELECT_MAX_VALUES = 25
COG_MAX_COMMANDS = 96


class KuriHelp(HelpCommand):
    context: KurisuContext

    def __init__(self):
        super().__init__(show_hidden=True)

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

            if len(commands) > COG_MAX_COMMANDS:  # Workaround some cogs having way too many commands, let's go gambling
                random.shuffle(commands)
                commands = commands[:COG_MAX_COMMANDS]
                commands.sort(key=lambda x: x.name)

            for batch in batched(commands, SELECT_MAX_VALUES - 1):
                view.add_item(CommandSelect(cog, list(batch), self.context,
                                            suffix=f"[{batch[0].name[0].upper()}-{batch[-1].name[0].upper()}]"))
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
