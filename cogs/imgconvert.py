import discord
import concurrent.futures
import functools

from discord import File
from discord.ext import commands
from io import BytesIO
from PIL import Image
from pillow_heif import HeifImagePlugin  # noqa: F401
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu

MAX_SIZE = (800, 600)
ALLOWED_EXTENSIONS = ('.bmp', '.heif', '.heic')


class ImageConvert(commands.Cog):
    """
    Convert images automatically.
    """

    def __init__(self, bot: 'Kurisu'):
        self.bot = bot

    @staticmethod
    def img_convert(in_img: bytes):
        img_obj = Image.open(BytesIO(in_img))
        img_obj.thumbnail(MAX_SIZE)
        img_out = BytesIO()
        img_obj.save(img_out, 'webp', lossless=False, quality=20)
        img_out.seek(0)
        return img_out

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # BMP and HEIF conversion
        for f in message.attachments:
            if f.filename.lower().endswith(ALLOWED_EXTENSIONS) and f.size <= 5242880:  # 5MiB
                async with self.bot.session.get(f.url, timeout=45) as img_request:
                    img_content = await img_request.read()
                    with concurrent.futures.ProcessPoolExecutor() as pool:
                        img_out = await self.bot.loop.run_in_executor(pool, functools.partial(self.img_convert, img_content))
                    out_message = f"{f.filename} from {message.author.mention}"
                    new_filename = f.filename.split('.')[0] + ".webp"
                    img = File(img_out, filename=new_filename)
                    await message.channel.send(file=img, content=out_message)


async def setup(bot):
    await bot.add_cog(ImageConvert(bot))
