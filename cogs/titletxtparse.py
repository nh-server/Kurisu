import discord
import concurrent.futures
import logging
import functools
import re

from discord.ext import commands, tasks
from discord import AllowedMentions, Member
from typing import TYPE_CHECKING

from codecs import BOM_UTF16_BE, BOM_UTF16_LE

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
_THEME_TIDLOWS = ["0004008c", "00009800", "000002cc", "00008f00", "000002cd", "000002ce"]

_TREE_INDENT = (
    " " * 3
)  # Windows TREE uses three spaces for indents, instead of the usual four
_TREE_DIRECTORY_RE = re.compile(r"[\\\+]---(.+)")
_TREE_FILE_RE = re.compile(r"[\| ]+(\S+)")

_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")

_TITLE_TXT_RE = re.compile(r"[TtIiLlEe]{4,}[^_]+\.[tx]{3,}")

_SAFE_MENTIONS = AllowedMentions(
    everyone=False, users=False, roles=False, replied_user=True
)


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
                directory[dir_name], fsflag_temp = parse_tree(lines[pos + 1:])
                if fs_corruption_flag is False and fsflag_temp is True:
                    # this should be burn-once and should never be set back to false once set to true
                    fs_corruption_flag = True
            else:
                directory[dir_name], fsflag_temp = parse_tree(lines[pos + 1:seek_pos])
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


class MultipleID1Exception(Exception):
    """
    Exception thrown when multiple ID1s are found
    """


class MangledFolderStructure(Exception):
    """
    Exception thrown if 00040000 is not found but other title folders are found
    Shouldn't happen unless helpee has deleted
    """


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
                # ...maybe two
                elif tidlow in _THEME_TIDLOWS:
                    name = "themes"  # intended to make the string "DLC for themes"... kludgy but user will get the idea

        return name

    @staticmethod
    def check_standard_titles(in_tree: dict) -> list[str]:
        """
        Parse a set of normal (non-DLC) titles
        """

        bad_titles = list()

        for title_id, title in in_tree.items():
            if not isinstance(title, dict):
                if _HEX_RE.match(title_id) and len(title_id) == 8:
                    # first observed 2025-04-11 12:32 3ds-assistance-2
                    # mystery title-like "files?" should be yeeted
                    bad_titles.append(title_id)
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
                    if ".tmd" in content_folder_id:
                        flag_tmd_ok = True
                    continue

                if not _HEX_RE.match(content_folder_id):
                    # not a hexadecimal name... may be cmd
                    continue

                if len(content_folder) == 0:
                    # karma says empty content folder on themes doesn't break HOME menu
                    if title_id not in _THEME_TIDLOWS:
                        bad_titles.append(title_id)
                        break

                for file in content_folder:
                    if ".app" in file:
                        flag_app_ok = True

            if title_id in bad_titles:
                # added to list inside content folder loop, skip to next TID
                continue

            if not (flag_app_ok and flag_tmd_ok):
                bad_titles.append(title_id)

        return bad_titles

    @staticmethod
    def detect_mangled_structure(in_tree: dict) -> bool:
        """
        Check for mangled folder structure in title folder
        """
        title_folder_count = 0
        for item_name in in_tree.keys():
            if len(item_name) == 8 and item_name.startswith("0004"):
                title_folder_count += 1

        if title_folder_count > 0:
            # helpee has mangled the Title folder, bail and request human intervention
            return True

        return False

    def bad_titles(self, in_tree: dict) -> dict | None:
        """
        Further examine the output of parse_dir to get a list of 3DS titles
        which may be missing data.

        Returns None if the 00040000 folder is missing (filename match may be a false positive)
        """

        if "00040000" not in in_tree:
            # this isn't the title folder... search for it
            result = self.find_title_folder(in_tree)
            if not result:
                # check for mangled folder structure
                if self.detect_mangled_structure(in_tree):
                    # helpee has mangled the Title folder, bail and request human intervention
                    raise MangledFolderStructure()
                else:
                    # nope, we're genuinely lost
                    return None
            else:
                in_tree = result

        # check again for mangled folder structure
        if "00040000" not in in_tree:
            if self.detect_mangled_structure(in_tree):
                raise MangledFolderStructure()

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

    @staticmethod
    def find_title_folder(directory: dict) -> dict:
        """
        Try to find the title folder if Tree wasn't run from there already
        """
        if "title" in directory:
            # tree was run from id1
            return directory["title"]

        if "Nintendo 3DS" in directory:
            # tree was run from root
            for id0_name, id0 in directory["Nintendo 3DS"].items():
                if isinstance(id0, dict) and _HEX_RE.match(id0_name):
                    if len(id0) > 1:
                        # uh oh, multiple ID1s, bail!
                        raise MultipleID1Exception(id0.keys())

                    for id1_name, id1 in id0.items():
                        if isinstance(id1, dict) and _HEX_RE.match(id1_name):
                            if "title" in id1:
                                return id1["title"]
                            else:
                                # no title folder... strange
                                return None

        for item_name, item in directory.items():
            if (
                isinstance(item, dict)
                and _HEX_RE.match(item_name)
                and len(item_name) > 8  # catch running from 00040000
            ):
                # id0 or id1
                for subitem_name, subitem in item.items():
                    if isinstance(subitem, dict) and subitem_name == "title":
                        # "item" was id1
                        return subitem

                # "item" is id0
                if len(item) > 1:
                    raise MultipleID1Exception(item.keys())

                for id1_name, id1 in item.items():

                    if "title" in id1:
                        return id1["title"]

        return None  # failsafe... what the hell have they done to their SD?

    @staticmethod
    def sanitize(input_str: str) -> str:
        """
        Sanitize a string (remove backticks, @ symbols, etc) to prevent exploits.
        """
        output_replacements = str.maketrans(
            {
                "@": "＠",  # full-width @ sign, won't trigger pings on Discord
                "`": "'",  # prevent escaping a code block
            }
        )

        return input_str.translate(output_replacements)

    @staticmethod
    def create_header(
        message: str, author: Member, filename: str = None, count: int = 1
    ) -> str:
        """
        Create a header that mentions the user and optionally
        mentions the filename if multiple files were attached
        """
        filename_safe = filename.translate(
            str.maketrans(
                {
                    "@": "＠",  # full-width @ sign, won't trigger pings on Discord
                    "`": "'",  # prevent escaping a code block
                }
            )
        )
        if count > 1:
            return f"{author.mention}: `{filename_safe}`: {message}"
        else:
            return f"{author.mention}: {message}"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Message handler for the TitleTXT parser cog.
        """
        attach_count = len(message.attachments)
        for f in message.attachments:
            if f.size > (20 * 1024 * 1024):
                # it should NEVER get to 20mb, but 20mb in RAM won't kill Kurisu
                # 500mb might thought
                continue
            if _TITLE_TXT_RE.match(f.filename):
                async with self.bot.session.get(f.url) as titletxt_request:
                    titletxt_content = await titletxt_request.read()
                    if titletxt_content[:2] in (BOM_UTF16_LE, BOM_UTF16_BE):
                        titletxt_lines = self.sanitize(
                            titletxt_content.decode(encoding="utf-16", errors="replace")
                        ).splitlines()
                    else:
                        titletxt_lines = self.sanitize(
                            titletxt_content.decode(encoding="utf-8", errors="replace")
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
                try:
                    bad_titles = self.bad_titles(parsed_tree)
                    bad_folders = self.bad_folders(parsed_tree)
                except MultipleID1Exception:
                    out_message = self.create_header(
                        "You appear to have multiple ID1 folders! ",
                        author=message.author,
                        filename=f.filename,
                        count=attach_count,
                    )
                    out_message += "Please [fix this](<https://wiki.hacks.guide/wiki/3DS:MID1>) and then try again."
                    await message.reply(out_message, allowed_mentions=_SAFE_MENTIONS)
                    continue
                except MangledFolderStructure:
                    out_message = self.create_header(
                        "The `00040000` folder, which contains game data, is missing, but you have other `0004xxxx` folders present. ",
                        author=message.author,
                        filename=f.filename,
                        count=attach_count,
                    )
                    out_message += "These folders contain non-game data, such as DLC. "
                    out_message += "You will need to either restore a backup of your SD card, or wait for further assistance."
                    await message.reply(out_message, allowed_mentions=_SAFE_MENTIONS)
                    continue

                if bad_titles is None:
                    continue

                if len(bad_titles) == 0:
                    # no issues found
                    out_message = self.create_header(
                        "This `title.txt` appears to be OK. Your HOME Menu issues are not likely to be caused by missing data.",
                        author=message.author,
                        filename=f.filename,
                        count=attach_count,
                    )
                    await message.reply(out_message, allowed_mentions=_SAFE_MENTIONS)
                    continue

                out_message = self.create_header(
                    "Missing data was found in this `title.txt` which may be causing issues.\n\n",
                    author=message.author,
                    filename=f.filename,
                    count=attach_count,
                )

                title_counter = 0
                total_title_count = sum(len(folder) for folder in bad_titles)

                for folder_name, folder in bad_titles.items():
                    out_message += f"Copy the following folders from the `{folder_name}` folder inside the `title` folder to your computer, then delete them from your SD card:\n"

                    for title in folder:
                        title_clean = title[:8]  # TIDs should only be eight characters anyway
                        title_name = self.get_name_by_tid(title_clean)
                        if title_name:
                            if folder_name == _DLC_TIDHIGH:
                                out_message += f"- `{title_clean}` (DLC for {title_name})\n"
                            else:
                                out_message += f"- `{title_clean}` ({title_name})\n"
                        else:
                            out_message += f"- `{title_clean}`\n"
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

                await message.reply(out_message, allowed_mentions=_SAFE_MENTIONS)


async def setup(bot):
    await bot.add_cog(TitleTXTParser(bot))
