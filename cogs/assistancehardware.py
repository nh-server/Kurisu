from __future__ import annotations

import logging
from os.path import dirname, join
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.mdcmd import add_md_files_as_commands
from utils.utils import KurisuCooldown, simple_embed

if TYPE_CHECKING:
    from kurisu import Kurisu
    from utils.context import KurisuContext

logger = logging.getLogger(__name__)

# Key must be lower case
consoles = {
    # Microsoft
    'xbox': 'https://www.ifixit.com/Device/Xbox',
    'xbox360': 'https://www.ifixit.com/Device/Xbox_360',
    'xbox360s': 'https://www.ifixit.com/Device/Xbox_360_S',
    'xbox360e': 'https://www.ifixit.com/Device/Xbox_360_E',
    'xbox1': 'https://www.ifixit.com/Device/Xbox_One',
    'xbox1s': 'https://www.ifixit.com/Device/Xbox_One_S',
    'xbox1sdigital': 'https://www.ifixit.com/Device/Xbox_One_S_All_Digital_Edition',
    'xbox1x': 'https://www.ifixit.com/Device/Xbox_One_X',
    'xboxseriess': 'https://www.ifixit.com/Device/Xbox_Series_S',
    'xboxseriesx': 'https://www.ifixit.com/Device/Xbox_Series_X',
    # Nintendo
    'nes': 'https://www.ifixit.com/Device/Nintendo_Entertainment_System',
    'snes': 'https://www.ifixit.com/Device/Super_Nintendo',
    'xbox360s': 'https://www.ifixit.com/Device/Xbox_360_S',
    'n64': 'https://www.ifixit.com/Device/Nintendo_64',
    'gamecube': 'https://www.ifixit.com/Device/Nintendo_GameCube',
    'famicondisk': 'https://www.ifixit.com/Device/Nintendo_Famicom_Disk_System',
    'famicon': 'https://www.ifixit.com/Device/Nintendo_Family_Computer_%28Famicom%29',
    'wii': 'https://www.ifixit.com/Device/Nintendo_Wii',
    'wiifamily': 'https://www.ifixit.com/Device/Nintendo_Wii_2011',
    'wiimini': 'https://www.ifixit.com/Device/Nintendo_Wii_mini',
    'wiiu': 'https://www.ifixit.com/Device/Nintendo_Wii_U',
    'gameboy': 'https://www.ifixit.com/Device/Game_Boy',
    'gameboyadvance': 'https://www.ifixit.com/Device/Game_Boy_Advance',
    'gameboyadvancesp': 'https://www.ifixit.com/Device/Nintendo_Game_Boy_Advance_SP',
    'gameboycolor': 'https://www.ifixit.com/Device/Game_Boy_Color',
    'gameboymicro': 'https://www.ifixit.com/Device/Game_Boy_Micro',
    'gameboypocket': 'https://www.ifixit.com/Device/Game_Boy_Pocket',
    'ds': 'https://www.ifixit.com/Device/Nintendo_DS',
    'dslite': 'https://www.ifixit.com/Device/Nintendo_DS_Lite',
    'dsi': 'https://www.ifixit.com/Device/Nintendo_DSi',
    'dsixl': 'https://www.ifixit.com/Device/Nintendo_DSi_XL',
    '2ds': 'https://www.ifixit.com/Device/Nintendo_2DS',
    '3ds': 'https://www.ifixit.com/Device/Nintendo_3DS',
    '3dsxl': 'https://www.ifixit.com/Device/Nintendo_3DS_XL',
    'new3ds': 'https://www.ifixit.com/Device/Nintendo_3DS_2015',
    'new3dsxl': 'https://www.ifixit.com/Device/Nintendo_3DS_XL_2015',
    'new2dsxl': 'https://www.ifixit.com/Device/New_Nintendo_2DS_XL',
    'switch': 'https://www.ifixit.com/Device/Nintendo_Switch',
    'switcholed': 'https://www.ifixit.com/Device/Nintendo_Switch_OLED_Model',
    'switchlite': 'https://www.ifixit.com/Device/Nintendo_Switch_Lite',
    'joycons': 'https://www.ifixit.com/Device/Joy-Con',
    'procontroller': 'https://www.ifixit.com/Device/Switch_Pro_Controller',
    'gamewatch': 'https://www.ifixit.com/Device/Game_Watch_Nintendo',
    'gameboylight': 'https://www.ifixit.com/Device/Game_Boy_Light',
    # Sega
    'segacd': 'https://www.ifixit.com/Device/Sega_CD',
    'dreamcast': 'https://www.ifixit.com/Device/Sega_Dreamcast',
    'gamegear': 'https://www.ifixit.com/Device/Sega_Game_Gear',
    'genesis': 'https://www.ifixit.com/Device/Sega_Genesis',
    'genesis2': 'https://www.ifixit.com/Device/Sega_Genesis_II',
    'saturn': 'https://www.ifixit.com/Device/Sega_Saturn',
    'genesis3': 'https://www.ifixit.com/Device/Sega_genesis_3',
    'mastersystem': 'https://www.ifixit.com/Device/Sega_Master_System',
    'mastersystem2': 'https://www.ifixit.com/Device/Sega_Master_System_II',
    'nomad': 'https://www.ifixit.com/Device/Sega_Nomad',
    # Sony
    'playstation': 'https://www.ifixit.com/Device/PlayStation',
    'playstation2': 'https://www.ifixit.com/Device/PlayStation_2',
    'playstation2slim': 'https://www.ifixit.com/Device/PlayStation_2_Slimline',
    'playstation2slim75x': 'https://www.ifixit.com/Device/PlayStation_2_Slimline_SCPH-7500x',
    'playstation2slime9x': 'https://www.ifixit.com/Device/PlayStation_2_Slimline_SCPH-9000X',
    'playstation3': 'https://www.ifixit.com/Device/PlayStation_3',
    'playstation3slim': 'https://www.ifixit.com/Device/PlayStation_3_Slim',
    'playstation3superslim': 'https://www.ifixit.com/Device/PlayStation_3_Super_Slim',
    'playstation4': 'https://www.ifixit.com/Device/PlayStation_4',
    'playstation4slim': 'https://www.ifixit.com/Device/PlayStation_4_Slim',
    'playstation4pro': 'https://www.ifixit.com/Device/PlayStation_4_Pro',
    'playstation5': 'https://www.ifixit.com/Device/PlayStation_5',
    'playstation5slim': 'https://www.ifixit.com/Device/PlayStation_5_Slim',
    'playstationslim': 'https://www.ifixit.com/Device/PlayStation_One',
    'pspe': 'https://www.ifixit.com/Device/PSP_E1000',
    'vita': 'https://www.ifixit.com/Device/PlayStation_Vita',
    'psportal': 'https://www.ifixit.com/Device/PlayStation_Portal',
    'vitaslim': 'https://www.ifixit.com/Device/PS_Vita_Slim',
    'psp1000': 'https://www.ifixit.com/Device/PSP_1000',
    'psp2000': 'https://www.ifixit.com/Device/PSP_2000',
    'psp3000': 'https://www.ifixit.com/Device/PSP_3000',
    'pspgo': 'https://www.ifixit.com/Device/PSP_Go',
    # Steam
    'steamdeck': 'https://www.ifixit.com/Device/Steam_Deck',
    'steamdeckoled': 'https://www.ifixit.com/Device/Steam_Deck_OLED',
    # Misc
    'wonderswan': 'https://www.ifixit.com/Device/Bandai_WonderSwan',
    'rog-ally': 'https://www.ifixit.com/Device/Asus_ROG_Ally',
}
# Key must be lower case
alias = {
    "xboxone": "xbox1",
    "xbox1sd": "xbox1sdigital",
    "wiifam": "wiifamily",
    "cube": "gamecube",
    "mini": "wiimini",
    "watch": "gamewatch",
    "gb": "gameboy",
    "gba": "gameboyadvance",
    "gbsp": "gameboyadvancesp",
    "sp": "gameboyadvancesp",
    "gbc": "gameboycolor",
    "color": "gameboycolor",
    "gbm": "gameboymicro",
    "micro": "gameboymicro",
    "pocket": "gameboypocket",
    "mgb": "gameboypocket",
    "light": "gameboypocket",
    "o3dsxl": "3dsxl",
    "n3ds": "new3ds",
    "n3dsxl": "new3dsxl",
    "red": "new3dsxl",
    "n2dsxl": "new2dsxl",
    "switcho": "switcholed",
    "oled": "switcholed",
    "lite": "switchlite",
    "gg": "gamegear",
    "ms": "mastersystem",
    "ps1": "playstation",
    "ps2": "playstation2",
    "ps3": "playstation3",
    "ps4": "playstation4",
    "ps5": "playstation5",
    "ps1slim": "playstationslim",
    "ps2slim": "playstation2slim",
    "ps3slim": "playstation3slim",
    "ps4slim": "playstation4slim",
    "ps5slim": "playstation5slim",
    "swan": "wonderswan",
    "ally": "rog-ally",
    "dmg": "gameboy",
    "agb": "gameboyadvance",
    "ags": "gameboyadvancesp",
    "cgb": "gameboycolor",
    "oxy": "gameboymicro",
    "ntr": "ds",
    "dsl": "dslite",
    "usg": "dslite",
    "twl": "dsi",
    "utl": "dsixl",
    "o2ds": "2ds",
    "ftr": "2ds",
    "o3ds": "3ds",
    "ctr": "3ds",
    "spr": "3dsxl",
    "ktr": "new3ds",
    "jan": "new2dsxl",
}

boards = {
    "dslite": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-dsl.png",
    "dsixl": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-dsixl.png",
    "o3ds": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-o3ds.jpg",
    "o3dsxl": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-o3dsxl.png",
    "n3ds": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-n3ds.png",
    "n3dsxl": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-n3dsxl.png",
    "n2dsxl": "https://hacksguidewiki.sfo3.digitaloceanspaces.com/hardwarewiki/Board-n2dsxl.png",
}


class AssistanceHardware(commands.Cog):
    """
    General hardware commands that will mostly be used in the hardware but also other help channels.
    """

    data_dir = join(dirname(__file__), 'assistance-cmds')

    def __init__(self, bot: Kurisu):
        self.bot: Kurisu = bot

    @commands.group(cooldown=None, invoke_without_command=True, case_insensitive=True)
    async def hardware(self, ctx: KurisuContext):
        """Links to one of multiple guides"""
        if isinstance(ctx.channel, discord.DMChannel) or ctx.channel == self.bot.channels['bot-cmds']:
            await ctx.send_help(ctx.command)
        else:
            await ctx.send(f'{ctx.author.mention}, if you wish to view the '
                           f'complete list of tutorials, send `.help hardware` to me in a {self.bot.channels["bot-cmds"]}.',
                           delete_after=10)

    @commands.dynamic_cooldown(KurisuCooldown(1, 5), commands.BucketType.channel)
    @commands.command()
    async def fix(self, ctx: KurisuContext, console=''):
        """Links to one of multiple ifixit guides"""
        console = console.lower()
        if console in consoles.keys():
            await simple_embed(ctx, consoles[console], color=discord.Color.blue())
        elif console in alias.keys():
            await simple_embed(ctx, consoles[alias[console]], color=discord.Color.blue())
        else:
            await simple_embed(ctx, "Invalid console, see https://www.ifixit.com/Device/Game_Console",
                               color=discord.Color.red())

    @commands.dynamic_cooldown(KurisuCooldown(1, 5), commands.BucketType.channel)
    @commands.command()
    async def board(self, ctx: KurisuContext, console: str = ""):
        """Board diagram for the given console."""
        console = console.lower()
        embed = discord.Embed(color=discord.Color.blue())

        if console in boards.keys():
            embed.set_image(url=boards[console])
        elif console in alias.keys() and alias[console] in boards.keys():
            embed.set_image(url=boards[alias[console]])
        else:
            embed.description = f'{ctx.author.mention}, Board options are `' + ', '.join(boards) + "`"
            embed.color = discord.Color.red()
            await ctx.send(embed=embed, delete_after=10)
            return

        embed.title = f"Board Diagram: {console.capitalize()}"
        await ctx.send(embed=embed)


add_md_files_as_commands(AssistanceHardware, join(AssistanceHardware.data_dir, 'hardware'),
                         namespace=AssistanceHardware.hardware)  # type: ignore


async def setup(bot):
    await bot.add_cog(AssistanceHardware(bot))
