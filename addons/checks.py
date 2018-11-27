from discord.ext import commands
import json

with open("data/staff.json", "r") as staff_file:
    staff = json.load(staff_file)
with open("data/helpers.json", "r") as helpers_file:
    helpers = json.load(helpers_file)
staff_rank = {"Owner": 0, "SuperOP": 1, "OP": 2, "HalfOP": 3, "Helper": 4}


def is_staff(role):
    def predicate(ctx):
        #just in case
        if ctx.message.server.owner == ctx.message.author:
            return True
        if role == "Helper":
            try:
                helpers[ctx.message.author.id]
                return True
            except:
                pass
        try:
            rank = staff_rank[staff[ctx.message.author.id]]
        except KeyError:
            return False
        return rank <= staff_rank[role]
    return commands.check(predicate)

def check_staff(id,role):
    if role == "Helper":
        try:
            helpers[id]
            return True
        except KeyError:
            pass
    try:
        rank = staff_rank[staff[id]]
    except KeyError:
        return False
    return rank <= staff_rank[role]
