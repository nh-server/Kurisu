from collections import defaultdict
from glob import iglob
from os.path import basename, dirname, join
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from utils.utils import ConsoleColor

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Type, Union
empty = discord.Embed.Empty

systems_no_aliases = ('3ds', 'wiiu', 'vwii', 'switch', 'wii', 'dsi', 'legacy')
aliases = {
    'nx': 'switch',
    'ns': 'switch'
}
name_to_aliases = defaultdict(set)
for k, v in aliases.items():
    name_to_aliases[v].add(k)

# compatibility
systems = systems_no_aliases + tuple(aliases)


def parse_header(header_raw: str):
    header: Dict[str, str] = {
        'title': empty,
        'url': empty,
        'author.name': None,
        'author.url': empty,
        'author.icon-url': empty,
        'help-desc': None,
        'aliases': '',
        'color': None,
        'thumbnail-url': empty,
    }

    for line in header_raw.splitlines():
        key, value = line.split(':', maxsplit=1)
        key = key.strip()
        value = value.strip()
        header[key] = value

    return header


def parse_body(body_raw: str):
    body_raw = body_raw.strip()
    # first one should be the descripton and will have no header
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

    return parts


def create_embed(header: 'Dict[str, str]', body: 'List[Tuple[str, str]]', embed_color: discord.Color):
    description = body[0][1]
    embed = discord.Embed(
        title=header['title'],
        description=description,
        url=header['url'],
        color=embed_color,
        thumbnail=None,
    )
    if header['author.name']:  # this field is required
        embed.set_author(name=header['author.name'], url=header['author.url'], icon_url=header['author.icon-url'])
    embed.set_thumbnail(url=header['thumbnail-url'])

    # first one is used as the embed description
    for field in body[1:]:
        embed.add_field(name=field[0], value=field[1], inline=False)

    return embed


def parse_md_command(md_text: str, embed_color: discord.Color):
    header_raw, body_raw = md_text.split('\n\n', maxsplit=1)

    header = parse_header(header_raw)
    body = parse_body(body_raw)

    if header['color']:
        # override with the custom color
        embed_color = discord.Color(int(header['color'], 16))

    return header, create_embed(header, body, embed_color)


def md_file_to_embed(md_path: str):
    colors = {
        '3ds': ConsoleColor.n3ds(),
        'wiiu': ConsoleColor.wiiu(),
        'vwii': ConsoleColor.wiiu(),
        'wii': ConsoleColor.wii(),
        'switch': ConsoleColor.switch(),
        'legacy': ConsoleColor.legacy(),
        'all': empty  # default embed color
    }

    with open(md_path, 'r', encoding='utf-8') as f:
        fn = basename(md_path)
        name, console, _ = fn.rsplit('.', maxsplit=2)
        return (name, console, *parse_md_command(f.read(), colors[console]))


def check_console(message, channel, consoles):
    message = message.lower()
    if message in consoles:
        return True
    elif ("wii" not in consoles or channel.startswith("legacy")) and channel.startswith(consoles) and message not in systems:
        return True
    return False


def get_console_name(console):
    return aliases.get(console, console)


def add_md_files_as_commands(cog_class: 'Type[commands.Cog]', md_dir: str = None, *, namespace=commands):

    def make_cmd(name: str, help_desc: 'Optional[str]', embeds: 'Dict[str, discord.Embed]', aliases: list):
        if len(embeds) > 1:
            # multi-console commands require a check
            async def cmd(self, ctx, *, consoles=''):
                supported_consoles = tuple(embeds)
                # replace aliases with the expected console
                requested_consoles = {get_console_name(c) for c in consoles.split()}
                # and then check if any of the consoles are supported here
                requested_consoles = {c for c in requested_consoles if c in supported_consoles}
                channel_name = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else ''

                if not requested_consoles:
                    if channel_name.startswith(supported_consoles):
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
                        if check_console(console, channel_name, embed_console):
                            await ctx.send(embed=embed)
        else:
            # single-console commands can simply print the one embed
            async def cmd(self, ctx):
                # this is kinda ugly, but basically it gets the first (and only) value of the dict
                await ctx.send(embed=next(iter(embeds.values())))

        parent = None
        if isinstance(namespace, commands.Group):
            parent = namespace

        cmd.__name__ = name
        # i figured this was easier than dealing with the multiple attributes for command help
        cmd.__doc__ = help_desc

        # this feels _wrong_ but is probably the best way to do this
        return namespace.command(name=name, aliases=aliases)(cmd)

    new_commands = defaultdict(dict)
    aliases = defaultdict(list)
    helpdescs = defaultdict(lambda: None)

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
    
    for command, embed_dict in new_commands.items():
        new_aliases = list(set(aliases[command]))
        command_obj = make_cmd(command, helpdescs[command], embed_dict, new_aliases)
        setattr(cog_class, command, command_obj)
        # there has to be a better way to do this...
        cog_class.__cog_commands__.append(command_obj)
