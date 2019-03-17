from discord.ext import commands
from cogs.database import DatabaseCog


staff_rank = {"Owner": 0, "SuperOP": 1, "OP": 2, "HalfOP": 3, "Helper": 4}
def is_staff(role):
    def predicate(ctx):
        return check_staff(ctx, role) if not ctx.author == ctx.guild.owner else True
    return commands.check(predicate)

def check_staff(ctx, role):
    if role == "Helper":
        if(DatabaseCog.get_console(ctx, ctx.author.id)):
            return True
    rank = DatabaseCog.get_stafftrole(ctx, ctx.author.id)
    if rank:
        return staff_rank[rank] <= staff_rank[role]
    return False
