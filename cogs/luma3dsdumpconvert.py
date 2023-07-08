import discord
import concurrent.futures
import functools

from discord.ext import commands
from struct import unpack_from
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu

# adapted from luma3ds_exception_dump_parser
handledExceptionNames = ("FIQ", "undefined instruction", "prefetch abort", "data abort")
registerNames = tuple("r{0}".format(i) for i in range(13)) + ("sp", "lr", "pc", "cpsr") + ("dfsr", "ifsr", "far") + ("fpexc", "fpinst", "fpinst2")
svcBreakReasons = ("(svcBreak: panic)", "(svcBreak: assertion failed)", "(svcBreak: user-related)")
faultStatusSources = {
    0b1: 'Alignment', 0b100: 'Instruction cache maintenance operation fault',
    0b1100: 'External Abort on translation - First-level', 0b1110: 'External Abort on translation - Second-level',
    0b101: 'Translation - Section', 0b111: 'Translation - Page', 0b11: 'Access bit - Section', 0b110: 'Access bit - Page',
    0b1001: 'Domain - Section', 0b1011: 'Domain - Page', 0b1101: 'Permission - Section', 0b1111: 'Permission - Page',
    0b1000: 'Precise External Abort', 0b10110: 'Imprecise External Abort', 0b10: 'Debug event'
}


class Luma3DSDumpConvert(commands.Cog):
    """
    Convert luma3ds exception dump files automatically.
    """

    def __init__(self, bot: 'Kurisu'):
        self.bot = bot

    @staticmethod
    def dump_convert(data: bytes):
        out_message = ""
        if unpack_from("<2I", data) != (0xdeadc0de, 0xdeadcafe):
            return "Invalid file format"

        version, processor, exceptionType, _, nbRegisters, codeDumpSize, stackDumpSize, additionalDataSize = unpack_from("<8I", data, 8)
        nbRegisters //= 4

        processor, coreId = processor & 0xffff, processor >> 16

        if version < (1 << 16) | 2:
            return "Incompatible format version"

        registers = unpack_from("<{0}I".format(nbRegisters), data, 40)
        codeOffset = 40 + 4 * nbRegisters
        codeDump = data[codeOffset:codeOffset + codeDumpSize]
        stackOffset = codeOffset + codeDumpSize
        # stackDump = data[stackOffset:stackOffset + stackDumpSize]
        addtionalDataOffset = stackOffset + stackDumpSize
        additionalData = data[addtionalDataOffset:addtionalDataOffset + additionalDataSize]

        if processor == 9:
            out_message += "Processor: Arm9\n"
        else:
            out_message += "Processor: Arm11 (core {0})\n".format(coreId)

        typeDetailsStr = ""
        if exceptionType == 2:
            if (registers[16] & 0x20) == 0 and codeDumpSize >= 4:
                instr = unpack_from("<I", codeDump[-4:])[0]
                if instr == 0xe12fff7e:
                    typeDetailsStr = " (kernel panic)"
                elif instr == 0xef00003c:
                    typeDetailsStr = " " + (svcBreakReasons[registers[0]] if registers[0] < 3 else "(svcBreak)")
            elif (registers[16] & 0x20) == 1 and codeDumpSize >= 2:
                instr = unpack_from("<I", codeDump[-4:])[0]
                if instr == 0xdf3c:
                    typeDetailsStr = " " + (svcBreakReasons[registers[0]] if registers[0] < 3 else "(svcBreak)")

        elif processor != 9 and (registers[20] & 0x80000000) != 0:
            typeDetailsStr = " (VFP exception)"

        out_message += "Exception type: {0}{1}\n".format("unknown" if exceptionType >= len(handledExceptionNames) else handledExceptionNames[exceptionType], typeDetailsStr)

        if processor == 11 and exceptionType >= 2:
            xfsr = registers[18] if exceptionType == 2 else registers[17]
            out_message += "Fault status: " + faultStatusSources[xfsr & 0xf] + "\n"

        if additionalDataSize != 0:
            if processor == 11:
                out_message += "Current process: {0} ({1:016x})\n".format(additionalData[:8].decode("ascii"), unpack_from("<Q", additionalData, 8)[0])
            else:
                out_message += "Arm9 RAM dump exist, size {0:x}\n".format(additionalDataSize)

        out_message += "\nRegister dump:\n"
        for i in range(0, nbRegisters - (nbRegisters % 2), 2):
            if i == 16:
                out_message += "\n"
            out_message += "{0:<8}{1:<12}{2:<8}{3:<12}\n".format(registerNames[i], "{0:08x}".format(registers[i]), registerNames[i+1], "{0:08x}".format(registers[i+1]))
        if nbRegisters % 2 == 1:
            if processor == 11 and exceptionType == 3:
                access_type = "Write" if registers[17] & (1 << 11) != 0 else "Read"
                out_message += "{0:<8}{1:<12}Access type: {2}\n".format(registerNames[nbRegisters - 1], "{0:08x}".format(registers[nbRegisters - 1]), access_type)
            else:
                out_message += "{0:<8}{1:<12}\n".format(registerNames[nbRegisters - 1], "{0:08x}".format(registers[nbRegisters - 1]))

        return out_message

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for f in message.attachments:
            if f.filename.lower().startswith("crash_dump_") and f.filename.lower().endswith(".dmp") and f.size <= 1048576:  # 1MiB, probobly overkill?
                async with self.bot.session.get(f.url, timeout=45) as dump_request:
                    dump_content = await dump_request.read()
                    with concurrent.futures.ProcessPoolExecutor() as pool:
                        dump_out = await self.bot.loop.run_in_executor(pool, functools.partial(self.dump_convert, dump_content))
                    out_message = f"{f.filename} from {message.author.mention}\n```{dump_out}```"
                    await message.channel.send(content=out_message)


async def setup(bot):
    await bot.add_cog(Luma3DSDumpConvert(bot))
