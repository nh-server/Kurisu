import aiohttp
import concurrent.futures
import functools

from discord import File
from discord.ext import commands
from io import BytesIO
from PIL import Image


class ImageConvert(commands.Cog):
    """
    Convert images automatically.
    """
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    @staticmethod
    def img_convert(in_img):
        img_obj = Image.open(BytesIO(in_img))
        img_out = BytesIO()
        img_obj.save(img_out, 'png')
        img_out.seek(0)
        return img_out

    @commands.Cog.listener()
    async def on_message(self, message):
        # BMP conversion
        for f in message.attachments:
            if f.filename.lower().endswith('.bmp') and f.size <= 600000:  # 600kb
                async with aiohttp.ClientSession() as session:
                    async with session.get(f.url, timeout=45) as img_request:
                        img_content = await img_request.read()
                        with concurrent.futures.ProcessPoolExecutor() as pool:
                            img_out = await self.bot.loop.run_in_executor(pool, functools.partial(self.img_convert, img_content))
                        out_message = f"{f.filename} from {message.author.mention}"
                        new_filename = f.filename[:-3] + "png"
                        img = File(img_out, filename=new_filename)
                        await message.channel.send(file=img, content=out_message)


def setup(bot):
    bot.add_cog(ImageConvert(bot))
