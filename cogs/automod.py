from __future__ import annotations

import discord

from discord import app_commands, AutoModRuleTriggerType, AutoModRule
from discord.ext import commands

from utils.checks import is_staff
from utils.views import AutoModRulesView

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.context import GuildContext


async def rules_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    assert interaction.guild is not None
    rules = await interaction.guild.fetch_automod_rules()

    if current:
        choices = []
        for rule in rules:
            if rule.trigger.type is AutoModRuleTriggerType.keyword and current in rule.name:
                choices.append(app_commands.Choice(name=rule.name, value=str(rule.id)))
        return choices
    else:
        return [app_commands.Choice(name=rule.name, value=str(rule.id)) for rule in rules
                if rule.trigger.type is AutoModRuleTriggerType.keyword]


class AutoModRuleTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> discord.AutoModRule:
        assert interaction.guild is not None
        try:
            return await interaction.guild.fetch_automod_rule(int(value))
        except discord.NotFound:
            raise app_commands.TransformerError("Automod rule not found.", discord.AppCommandOptionType.string, self)


@app_commands.default_permissions(ban_members=True)
class AutoMod(commands.GroupCog):

    @is_staff("SuperOP")
    @commands.command()
    async def automod(self, ctx: GuildContext):
        """Sends a discord view to view and set some AutoMod rules settings."""
        rules = await ctx.guild.fetch_automod_rules()
        view = AutoModRulesView(rules, ctx.author)
        await ctx.send(embed=view.default_embed, view=view)

    @app_commands.autocomplete(rule=rules_autocomplete)
    @app_commands.guild_only
    @app_commands.command()
    async def add_keyword(self, interaction: discord.Interaction,
                          rule: app_commands.Transform[AutoModRule, AutoModRuleTransformer], keyword: str,
                          regex: bool = False):
        """Adds a keyword to an automod rule.

        Args:
            rule: ID of the AutoMod rule to add keyword, use autocomplete for this.
            keyword: Keyword to add to the AutoMod rule.
            regex: If the keyword is a regex expression.
        """
        assert interaction.guild is not None

        if rule.trigger.type != AutoModRuleTriggerType.keyword:
            await interaction.response.send_message("This automod rule doesn't have a keyword filter.", ephemeral=True)
            return

        if regex:
            if keyword in rule.trigger.regex_patterns:
                await interaction.response.send_message("This regex expression is already in the filter.",
                                                        ephemeral=True)
                return
            rule.trigger.regex_patterns.append(keyword)
        else:
            if keyword in rule.trigger.keyword_filter:
                await interaction.response.send_message("This keyword is already in the filter.", ephemeral=True)
                return
            rule.trigger.keyword_filter.append(keyword)

        try:
            await rule.edit(trigger=rule.trigger)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Failed to add keyword: {e}.", ephemeral=True)
            return
        await interaction.response.send_message(f"Added keyword {keyword} to {rule.name} Automod rule succesfully.",
                                                ephemeral=True)

    @app_commands.autocomplete(rule=rules_autocomplete)
    @app_commands.guild_only
    @app_commands.command()
    async def delete_keyword(self, interaction: discord.Interaction,
                             rule: app_commands.Transform[AutoModRule, AutoModRuleTransformer], keyword: str,
                             regex: bool = False):
        """Deletes a keyword from an AutoMod rule.

        Args:
            rule: ID of the AutoMod rule to remove keyword from, use autocomplete for this.
            keyword: Keyword to remove from the AutoMod rule.
            regex: If the keyword is a regex expression.
        """

        if rule.trigger.type != AutoModRuleTriggerType.keyword:
            await interaction.response.send_message("This AutoMod rule doesn't have a keyword filter.", ephemeral=True)
            return

        if regex:
            if keyword not in rule.trigger.regex_patterns:
                await interaction.response.send_message("This regex expression is not in the filter.", ephemeral=True)
                return
            rule.trigger.regex_patterns.remove(keyword)
        else:
            if keyword not in rule.trigger.keyword_filter:
                await interaction.response.send_message("This keyword is not in the filter.", ephemeral=True)
                return
            rule.trigger.keyword_filter.remove(keyword)

        try:
            await rule.edit(trigger=rule.trigger)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Failed to delete keyword: {e}.", ephemeral=True)
            return
        await interaction.response.send_message(f"Deleted keyword {keyword} from {rule.name} automod rule succesfully.",
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
