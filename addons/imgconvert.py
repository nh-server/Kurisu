from io import BytesIO
import aiohttp
import concurrent.futures
import functools
from PIL import Image

class ImageConvert:
    """
    Convert images automatically.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @staticmethod
    def img_convert(in_img):
        img_obj = Image.open(BytesIO(in_img))
        img_out = BytesIO()
        img_obj.save(img_out, 'png')
        img_out.seek(0)
        return img_out

    async def on_message(self, message):
        # BMP conversion
        for f in message.attachments:
            if f["filename"].lower().endswith('.bmp') and f["size"] <= 600000:  # 600kb
                async with aiohttp.ClientSession() as session:
                    async with session.get(f["url"], timeout=45) as img_request:
                        img_content = await img_request.read()
                        with concurrent.futures.ProcessPoolExecutor() as pool:
                            img_out = await self.bot.loop.run_in_executor(pool, functools.partial(self.img_convert, img_content))
                        out_message = "{} from {}".format(self.bot.escape_name(f["filename"]), message.author.mention)
                        new_filename = f["filename"][:-3] + "png"
                        await self.bot.send_file(message.channel, img_out, filename=new_filename, content=out_message)

def setup(bot):
    bot.add_cog(ImageConvert(bot))
