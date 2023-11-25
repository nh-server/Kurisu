import discord
import concurrent.futures
import functools

from discord.ext import commands
from struct import unpack_from
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu

# adapted from luma3ds_exception_dump_parser
handled_exception_names = ("FIQ", "undefined instruction", "prefetch abort", "data abort")
register_names = tuple("r{0}".format(i) for i in range(13)) + ("sp", "lr", "pc", "cpsr") + ("dfsr", "ifsr", "far") + ("fpexc", "fpinst", "fpinst2")
svc_break_reasons = ("(svcBreak: panic)", "(svcBreak: assertion failed)", "(svcBreak: user-related)")
fault_status_sources = {
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

        version, processor, exception_type, _, nb_registers, code_dump_size, stack_dump_size, additional_data_size = unpack_from("<8I", data, 8)
        nb_registers //= 4

        processor, core_id = processor & 0xffff, processor >> 16

        if version < (1 << 16) | 2:
            return "Incompatible format version"

        registers = unpack_from("<{0}I".format(nb_registers), data, 40)
        code_offset = 40 + 4 * nb_registers
        code_dump = data[code_offset:code_offset + code_dump_size]
        stack_offset = code_offset + code_dump_size
        # stackDump = data[stackOffset:stackOffset + stackDumpSize]
        addtional_data_offset = stack_offset + stack_dump_size
        additional_data = data[addtional_data_offset:addtional_data_offset + additional_data_size]

        if processor == 9:
            out_message += "Processor: Arm9\n"
        else:
            out_message += "Processor: Arm11 (core {0})\n".format(core_id)

        type_details_str = ""
        if exception_type == 2:
            if (registers[16] & 0x20) == 0 and code_dump_size >= 4:
                instr = unpack_from("<I", code_dump[-4:])[0]
                if instr == 0xe12fff7e:
                    type_details_str = " (kernel panic)"
                elif instr == 0xef00003c:
                    type_details_str = " " + (svc_break_reasons[registers[0]] if registers[0] < 3 else "(svcBreak)")
            elif (registers[16] & 0x20) == 1 and code_dump_size >= 2:
                instr = unpack_from("<I", code_dump[-4:])[0]
                if instr == 0xdf3c:
                    type_details_str = " " + (svc_break_reasons[registers[0]] if registers[0] < 3 else "(svcBreak)")

        elif processor != 9 and (registers[20] & 0x80000000) != 0:
            type_details_str = " (VFP exception)"

        out_message += "Exception type: {0}{1}\n".format("unknown" if exception_type >= len(handled_exception_names) else handled_exception_names[exception_type], type_details_str)

        if processor == 11 and exception_type >= 2:
            xfsr = registers[18] if exception_type == 2 else registers[17]
            out_message += "Fault status: " + fault_status_sources[xfsr & 0xf] + "\n"

        if additional_data_size != 0:
            if processor == 11:
                out_message += "Current process: {0} ({1:016x})\n".format(additional_data[:8].decode("ascii"), unpack_from("<Q", additional_data, 8)[0])
            else:
                out_message += "Arm9 RAM dump exist, size {0:x}\n".format(additional_data_size)

        out_message += "\nRegister dump:\n"
        for i in range(0, nb_registers - (nb_registers % 2), 2):
            if i == 16:
                out_message += "\n"
            out_message += "{0:<8}{1:<12}{2:<8}{3:<12}\n".format(register_names[i], "{0:08x}".format(registers[i]), register_names[i + 1], "{0:08x}".format(registers[i + 1]))
        if nb_registers % 2 == 1:
            if processor == 11 and exception_type == 3:
                access_type = "Write" if registers[17] & (1 << 11) != 0 else "Read"
                out_message += "{0:<8}{1:<12}Access type: {2}\n".format(register_names[nb_registers - 1], "{0:08x}".format(registers[nb_registers - 1]), access_type)
            else:
                out_message += "{0:<8}{1:<12}\n".format(register_names[nb_registers - 1], "{0:08x}".format(registers[nb_registers - 1]))

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
