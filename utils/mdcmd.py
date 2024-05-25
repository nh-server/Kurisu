from collections import defaultdict
from glob import iglob
from os.path import basename, join
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from utils.utils import ConsoleColor, KurisuCooldown

if TYPE_CHECKING:
    from typing import Optional, Type
    from cogs.assistance import Assistance
    from cogs.assistancewii import AssistanceWii
    from cogs.assistancewiiu import AssistanceWiiU
    from cogs.assistance3ds import Assistance3DS
    from cogs.assistanceswitch import AssistanceSwitch
    AssistanceCogs = Assistance | AssistanceWii | AssistanceWiiU | Assistance3DS | AssistanceSwitch

systems_no_aliases = ('3ds', 'wiiu', 'vwii', 'switch', 'wii', 'dsi', 'gba')
aliases = {
    'nx': 'switch',
    'ns': 'switch'
}
system_ignore_filter = ('all', 'vwii')
name_to_aliases = defaultdict(set)
for k, v in aliases.items():
    name_to_aliases[v].add(k)

# compatibility
systems = systems_no_aliases + tuple(aliases) + ('legacy',)

format_map = {
    'nx_firmware': '18.0.0',
    'ams_ver': '1.6.2',
    'hekate_ver': '6.1.0',
    'last_revision': '26th March, 2024',
}


def parse_header(header_raw: str) -> 'dict[str, Optional[str]]':
    header: dict[str, Optional[str]] = {
        'title': None,
        'url': None,
        'author.name': None,
        'author.url': None,
        'author.icon-url': None,
        'help-desc': None,
        'aliases': '',
        'color': None,
        'thumbnail-url': None,
        'image-url': None,
        'cooldown-rate': '1',
        'cooldown-per': '30',
    }

    for line in header_raw.splitlines():
        if line.startswith('---'):
            continue
        key, value = line.split(':', maxsplit=1)
        key = key.strip()
        value = value.strip()
        header[key] = value

    return header


def parse_body(body_raw: str):
    body_raw = body_raw.strip()
    # first one should be the description and will have no header
    parts = []
    current_header = ''
    current_body = []

    def doadd():
        parts.append((current_header, '\n'.join(current_body)))

    for line in body_raw.splitlines():
        if line.startswith('#'):
            # This does not work entirely how markdown should work.
            # It seems a header requires a space between the # and the text.
            # Example: "#test" should not work but "# test" does.
            # This isn't really worth trying to check for however.
            doadd()
            current_header = line.lstrip('#').lstrip(' ')
            current_body = []
        else:
            current_body.append(line)

    if current_header or current_body:
        doadd()

    # special case for an empty body
    if not parts:
        parts.append(('', ''))

    return parts


def create_embed(header: 'dict[str, Optional[str]]', body: 'list[tuple[str, str]]', embed_color: discord.Color):
    description = body[0][1]
    embed = discord.Embed(
        title=header['title'],
        description=description,
        url=header['url'],
        color=embed_color,
    )
    if header['author.name']:  # this field is required
        embed.set_author(name=header['author.name'], url=header['author.url'], icon_url=header['author.icon-url'])
    embed.set_thumbnail(url=header['thumbnail-url'])
    embed.set_image(url=header['image-url'])

    # first one is used as the embed description
    for field in body[1:]:
        embed.add_field(name=field[0], value=field[1], inline=False)

    return embed


def parse_md_command(md_text: str, embed_color: discord.Color) -> tuple[dict, discord.Embed]:
    parts = md_text.split('\n\n', maxsplit=1)
    if len(parts) == 1:
        # in case there is nobody
        parts.append('')
    header_raw, body_raw = parts

    body_raw = body_raw.format_map(format_map)

    header = parse_header(header_raw)
    body = parse_body(body_raw)

    if header['color']:
        # override with the custom color
        embed_color = discord.Color(int(header['color'], 16))

    return header, create_embed(header, body, embed_color)


def md_file_to_embed(md_path: str) -> tuple[str, str, dict, discord.Embed]:
    colors = {
        '3ds': ConsoleColor.n3ds(),
        'wiiu': ConsoleColor.wiiu(),
        'vwii': ConsoleColor.wiiu(),
        'wii': ConsoleColor.wii(),
        'switch': ConsoleColor.switch(),
        'legacy': ConsoleColor.legacy(),
        'dsi': ConsoleColor.legacy(),
        'gba': None,
        'all': None  # default embed color
    }

    with open(md_path, 'r', encoding='utf-8') as f:
        fn = basename(md_path)
        name, console, _ = fn.rsplit('.', maxsplit=2)
        header, embed = parse_md_command(f.read(), colors[console])
        return name, console, header, embed


def check_console(message, channel, consoles):
    message = message.lower()
    if isinstance(consoles, str):
        consoles = (consoles,)
    if message in consoles:
        return True
    elif channel.startswith(tuple(f"{c}-" for c in consoles)) and message not in systems:
        return True
    return False


def get_console_name(console):
    return aliases.get(console, console)


def add_md_files_as_commands(cog_class: 'Type[AssistanceCogs]', md_dir: str = None, *, namespace=commands, console_cmd: str = None):

    def make_cmd(name: str, help_desc: 'Optional[str]', embeds: 'dict[str, discord.Embed]', cooldown: 'tuple[int, int]', aliases: list[str]) -> commands.Command:
        if len(embeds) > 1:
            # multi-console commands require a check
            async def multi_cmd(self, ctx: commands.Context, *, consoles: str = ''):
                supported_consoles = list(embeds)
                for s in supported_consoles:
                    if s in {'dsi'}:
                        # special case for legacy channel
                        supported_consoles.append('legacy')
                # replace aliases with the expected console
                requested_consoles = {get_console_name(c) for c in consoles.split()}
                # and then check if any of the consoles are supported here
                requested_consoles = {c.lower() for c in requested_consoles if c.lower() in supported_consoles}
                channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ''

                if not requested_consoles:
                    if channel_name.startswith(tuple(supported_consoles)):
                        requested_consoles = {'auto'}
                    else:
                        valid = set(supported_consoles)
                        for v in supported_consoles:
                            valid |= name_to_aliases[v]
                        await ctx.send(f'Please specify a console. Valid options are: {", ".join(sorted(valid))}')

                        ctx.command.reset_cooldown(ctx)
                        return

                for console in requested_consoles:
                    for embed_console, embed in embeds.items():
                        cons = [embed_console]
                        if embed_console in {'dsi'}:
                            # special case for legacy channel
                            cons.append('legacy')
                        if check_console(console, channel_name, tuple(cons)):
                            await ctx.send(embed=embed, reference=ctx.message.reference, mention_author=any(ctx.message.mentions))
            cmd = multi_cmd
        else:
            # single-console commands can simply print the one embed
            async def simple_cmd(self, ctx: commands.Context):
                # this is kinda ugly, but basically it gets the first (and only) value of the dict
                await ctx.send(embed=next(iter(embeds.values())), reference=ctx.message.reference, mention_author=any(ctx.message.mentions))
            cmd = simple_cmd

        # I've to trick the lib, so it thinks the callback is inside a class
        cmd.__name__ = name
        cmd.__qualname__ = f"{cog_class.qualified_name}.{cmd.__name__}"

        # I figured this was easier than dealing with the multiple attributes for command help
        cmd.__doc__ = help_desc

        # this feels _wrong_ but is probably the best way to do this
        cooldown = commands.dynamic_cooldown(KurisuCooldown(cooldown[0], cooldown[1]), commands.BucketType.channel)(cmd)
        cmd_obj = namespace.command(name=name, aliases=aliases)(cooldown)
        return cmd_obj

    new_commands: 'dict[str, dict[str, discord.Embed]]' = defaultdict(dict)
    aliases: 'dict[str, list[str]]' = defaultdict(list)
    cooldowns: 'dict[str, tuple[int, int]]' = {}
    helpdescs: 'dict[str, Optional[str]]' = defaultdict(lambda: None)

    if md_dir is None:
        md_dir = cog_class.data_dir

    for md in iglob(join(md_dir, '*.md')):
        command, console, header, embed = md_file_to_embed(md)
        new_commands[command][console] = embed
        if header['aliases']:
            aliases[command].extend(header['aliases'].split(','))
        if header['help-desc']:
            # in case some don't have a help-desc, don't delete a previous one
            helpdescs[command] = header['help-desc']
        cooldowns[command] = (int(header['cooldown-rate']), int(header['cooldown-per']))

    # the tutorial subdirectory doesn't need console filtering
    filter_cmds = "tutorial" not in md_dir

    for command, embed_dict in new_commands.items():
        if filter_cmds:
            if console_cmd:
                if embed_dict.get(console_cmd) is None or len(embed_dict) > 1:
                    continue
            elif len(embed_dict) == 1 and not any(x in embed_dict for x in system_ignore_filter):
                continue
        new_aliases = list(set(aliases[command]))
        command_obj = make_cmd(command, helpdescs[command], embed_dict, cooldowns[command], new_aliases)
        setattr(cog_class, command, command_obj)
        # there has to be a better way to do this...
        cog_class.__cog_commands__.append(command_obj)
