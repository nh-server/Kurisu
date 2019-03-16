from discord.ext import commands
import json

with open("data/staff.json", "r") as staff_file:
    staff = json.load(staff_file)
with open("data/helpers.json", "r") as helpers_file:
    helpers = json.load(helpers_file)

staff_rank = {"Owner": 0, "SuperOP": 1, "OP": 2, "HalfOP": 3, "Helper": 4}

def is_staff(role):
    def predicate(ctx):
        return check_staff(ctx.author.id, role) if not ctx.author == ctx.guild.owner else True
    return commands.check(predicate)

def check_staff(id,role):
    if role == "Helper":
        try:
            helpers[str(id)]
            return True
        except KeyError:
            pass
    try:
        rank = staff_rank[staff[str(id)]]
    except KeyError:
        return False
    return rank <= staff_rank[role]
