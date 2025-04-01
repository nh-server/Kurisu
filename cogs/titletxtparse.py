import discord
import concurrent.futures
import logging
import functools
import re

from discord.ext import commands, tasks
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if TYPE_CHECKING:
    from kurisu import Kurisu

# max number of broken titles before we bail
# the most i've seen IRL on a non-dead card was about 5-6
_MAX_BROKEN_TITLES = 10

_DLC_TIDHIGH = "0004008c"
_STREETPASS_TIDLOWS = [
    "00020800",  # JPN
    "00021800",  # USA
    "00022800",  # EUR
    "00026800",  # CHN
    "00027800",  # KOR
    "00028800",  # TWN
]

_TREE_INDENT = (
    " " * 3
)  # Windows TREE uses three spaces for indents, instead of the usual four
_TREE_DIRECTORY_RE = re.compile(r"[\\\+]---(\S+)")
_TREE_FILE_RE = re.compile(r"[\| ]+(\S+)")

_HEX_RE = re.compile(r"[0-9a-fA-F]")

_TITLE_TXT_RE = re.compile(r"[TtIiLlEe]{4,}.+\.[tx]{3,}")


def parse_tree(lines: list[str]) -> tuple[dict, bool]:
    """
    Parse a directory recursively and return a dictionary representing its contents
    """
    directory = {}
    pos = 0
    fs_corruption_flag = False
    while pos < len(lines):
        line = lines[pos].rstrip()
        line_indent_level = line.count(_TREE_INDENT)
        if matchobj := _TREE_DIRECTORY_RE.search(line):
            dir_name = matchobj.group(1)
            # seek ahead to find next directory entry
            seek_pos = pos + 1
            while seek_pos < len(lines):
                seek_line = lines[seek_pos]
                seek_match_obj = _TREE_DIRECTORY_RE.search(seek_line)
                if seek_match_obj:
                    seek_indent_level = seek_line.count(_TREE_INDENT)
                    if seek_indent_level <= line_indent_level:
                        break
                    seek_pos = seek_pos + 1
                else:
                    seek_pos = seek_pos + 1
            if seek_pos >= len(lines):
                directory[dir_name], fsflag_temp = parse_tree(lines[pos + 1 :])
                if fs_corruption_flag is False and fsflag_temp is True:
                    # this should be burn-once and should never be set back to false once set to true
                    fs_corruption_flag = True
            else:
                directory[dir_name], fsflag_temp = parse_tree(lines[pos + 1 : seek_pos])
                if fs_corruption_flag is False and fsflag_temp is True:
                    # this should be burn-once and should never be set back to false once set to true
                    fs_corruption_flag = True

            pos = seek_pos - 1
        elif matchobj := _TREE_FILE_RE.match(line):
            file_name = matchobj.group(1)
            if file_name != "|":
                directory[file_name] = "(file)"
        elif line.replace("|", "").strip() == "":
            # ignore empty lines
            pass
        else:
            # mystery line
            # usually caused by filesystem corruption (\n in filename doesn't happen normally)
            fs_corruption_flag = True
        pos = pos + 1

    return directory, fs_corruption_flag


class TitleTXTParser(commands.Cog):
    """
    Parse the output of the Tree command (as suggested by the missingtitles tag)
    and reply with a list of corrupted titles which should be removed
    """

    def __init__(self, bot: "Kurisu"):
        self.bot = bot
        self.titledb = []
        self.hbdb = []
        self.tidpull.start()  # Title database code pulled from db3ds
        self.hbpull.start()

    async def cog_unload(self):
        self.tidpull.cancel()
        self.hbpull.cancel()

    @tasks.loop(hours=1)
    async def tidpull(self):
        regions = ["GB", "JP", "KR", "TW", "US"]
        titledb = []
        for region in regions:
            async with self.bot.session.get(
                f"https://raw.githubusercontent.com/hax0kartik/3dsdb/master/jsons/list_{region}.json"
            ) as r:
                if r.status == 200:
                    j = await r.json(content_type=None)
                    titledb = titledb + j
                else:
                    # if any of the JSONs can't be pulled, don't update
                    # otherwise, it could replace the db with nothing,
                    # and old data is better than no data
                    return
        self.titledb = titledb

    @tasks.loop(hours=1)
    async def hbpull(self):
        async with self.bot.session.get(
            "https://db.universal-team.net/data/full.json"
        ) as r:
            if r.status == 200:
                logging.debug("homebrew database is ready")
                self.hbdb = await r.json(content_type=None)
            else:
                # old data better than no data
                return

    def get_game_by_tid(self, tidlow: str, tidhigh: str = "00040000") -> str | None:
        """
        Get a title's name by it's TIDlow, as used in the 3DS folder structure
        """
        full_tid = tidhigh.upper() + tidlow.upper()
        for title in self.titledb:
            if title["TitleID"] == full_tid:
                return title["Name"]

        return None

    def get_hb_by_tidlow(self, tidlow: str) -> str | None:
        """
        Get a homebrew app's name by it's TIDlow
        """
        for title in self.hbdb:
            if "systems" in title and "3DS" in title["systems"]:
                if "unique_ids" in title:
                    for uid in title["unique_ids"]:
                        if f"{uid:x}" in tidlow:  # padding can get funky...
                            return title["title"]

        return None

    def get_name_by_tid(self, tidlow: str, tidhigh: str = "00040000") -> str | None:
        """
        Try both the homebrew and game databases
        """
        name = self.get_game_by_tid(tidlow, tidhigh)
        if name is None:
            name = self.get_hb_by_tidlow(tidlow)
            if name is None:
                # exactly one system title received DLC... StreetPass Mii Plaza
                # this is not counted as a release by 3dsdb, so it needs to be handled as a special case
                if tidlow in _STREETPASS_TIDLOWS:
                    name = "StreetPass Mii Plaza"

        return name

    @staticmethod
    def check_standard_titles(in_tree: dict) -> list[str]:
        """
        Parse a set of normal (non-DLC) titles
        """

        bad_titles = list()

        for title_id, title in in_tree.items():
            if not isinstance(title, dict):
                continue

            flag_ticket_ok = False
            flag_app_ok = False
            if "content" not in title:
                bad_titles.append(title_id)
                continue

            if "cmd" in title:
                if len(title["cmd"]) == 0:
                    # suggested by tophatted
                    # empty cmd folder may cause issues
                    bad_titles.append(title_id)
                    continue

            for content_item_name in title["content"]:
                if ".app" in content_item_name:
                    flag_app_ok = True
                elif ".tmd" in content_item_name:
                    flag_ticket_ok = True

            if not (flag_app_ok and flag_ticket_ok):
                bad_titles.append(title_id)

        return bad_titles

    @staticmethod
    def check_dlc_titles(in_tree: dict) -> list[str]:
        """
        Parse a set of DLC titles.
        The structure is different compared to normal titles, so special logic is required.
        """

        bad_titles = list()

        for title_id, title in in_tree.items():
            if "content" not in title:
                bad_titles.append(title_id)
                continue

            if "cmd" in title["content"]:
                if len(title["content"]["cmd"]) == 0:
                    bad_titles.append(title_id)
                    continue

            flag_app_ok = False
            flag_tmd_ok = False
            for content_folder_id, content_folder in title["content"].items():
                if not isinstance(content_folder, dict):
                    # file, maybe tmd
                    if ".tmd" in content_folder:
                        flag_tmd_ok = True
                    continue

                if not _HEX_RE.match(content_folder_id):
                    # not a hexadecimal name... may be cmd
                    continue

                if len(content_folder) == 0:
                    bad_titles.append(title_id)
                    break

                for file in content_folder:
                    if ".app" in file:
                        flag_app_ok = True

            if title_id in bad_titles:
                # set inside content loop check, break again here
                break

            if not (flag_app_ok and flag_tmd_ok):
                bad_titles.append(title_id)

        return bad_titles

    def bad_titles(self, in_tree: dict) -> list[str] | None:
        """
        Further examine the output of parse_dir to get a list of 3DS titles
        which may be missing data.

        Returns None if the 00040000 folder is missing (filename match may be a false positive)
        """

        if "00040000" not in in_tree:
            return None

        bad_titles = dict()
        for folder_name, folder in in_tree.items():
            if not isinstance(folder, dict):
                continue

            if not folder_name.startswith("0004"):
                continue

            if folder_name == _DLC_TIDHIGH:
                # dlc, special case
                bad_titles_for_folder = self.check_dlc_titles(folder)
                if len(bad_titles_for_folder) > 0:
                    bad_titles[folder_name] = bad_titles_for_folder

            else:
                bad_titles_for_folder = self.check_standard_titles(folder)
                if len(bad_titles_for_folder) > 0:
                    bad_titles[folder_name] = bad_titles_for_folder

        return bad_titles

    @staticmethod
    def bad_folders(directory: dict) -> list[str]:
        """
        Check for empty folders which may be causing issues
        """
        bad_folders = []
        for name, entry in directory.items():
            if isinstance(entry, dict):
                if len(entry) == 0:
                    bad_folders.append(name)

        return bad_folders

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Message handler for the TitleTXT parser cog.
        """
        for f in message.attachments:
            if _TITLE_TXT_RE.match(f.filename):
                async with self.bot.session.get(f.url, timeout=45) as titletxt_request:
                    titletxt_content = await titletxt_request.read()
                    titletxt_lines = titletxt_content.decode(
                        encoding="utf-16"
                    ).splitlines()
                    with concurrent.futures.ProcessPoolExecutor() as pool:
                        parsed_tree, fs_corruption_flag = (
                            await self.bot.loop.run_in_executor(
                                pool,
                                functools.partial(
                                    parse_tree, titletxt_lines[3:]
                                ),  # skip the first three lines - header and volume info
                            )
                        )
                bad_titles = self.bad_titles(parsed_tree)
                bad_folders = self.bad_folders(parsed_tree)

                if bad_titles is None:
                    # Happens if no "00040000" folder is found
                    out_message = f"{message.author.mention} This doesn't look correct. Are you sure you're running the `tree` command in the right folder?"
                    await message.reply(out_message)
                    return

                if len(bad_titles) == 0:
                    # no issues found
                    out_message = f"{message.author.mention} This `title.txt` appears to be OK. Your HOME Menu issues are not likely to be caused by missing data."
                    await message.reply(out_message)
                    return

                out_message = f"{message.author.mention} Missing data was found in this `title.txt` which may be causing issues.\n\n"
                title_counter = 0
                total_title_count = sum(len(folder) for folder in bad_titles)

                for folder_name, folder in bad_titles.items():
                    out_message += f"Copy the following folders from the `{folder_name}` folder inside the `title` folder to your computer, then delete them from your SD card:\n"

                    for title in folder:
                        title_name = self.get_name_by_tid(title)
                        if title_name:
                            if folder_name == _DLC_TIDHIGH:
                                out_message += f"- `{title}` (DLC for {title_name})\n"
                            else:
                                out_message += f"- `{title}` ({title_name})\n"
                        else:
                            out_message += f"- `{title}`\n"
                        title_counter += 1

                        if title_counter > _MAX_BROKEN_TITLES:
                            remaining = total_title_count - title_counter
                            out_message += f"...and {remaining} more "
                            out_message += " (send another title.txt once you've removed the above folders for more info)\n"
                            break

                    if title_counter > _MAX_BROKEN_TITLES:
                        break

                if len(bad_folders) > 0:
                    out_message += "Delete the following folders from the `title` folder (no need to copy first):\n"
                    for bad_folder in bad_folders:
                        out_message += f"- `{bad_folder}`\n"

                if fs_corruption_flag:
                    out_message += "\nAdditionally, your SD card appears to contain corrupted data. "
                    out_message += "We recommend making a backup of your card, then [checking it for issues](https://wiki.hacks.guide/wiki/Checking_SD_card_integrity).\n"

                out_message += "\nOnce you have completed these steps, re-insert the card into your console, and check to see if the HOME Menu loads correctly.\n"
                out_message += "If not, come back for further assistance, and mention that you have already tried the missingtitles steps."

                await message.reply(out_message)


async def setup(bot):
    await bot.add_cog(TitleTXTParser(bot))
