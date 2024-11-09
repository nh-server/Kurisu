import discord

from discord import ui, Embed
from utils.utils import gen_color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kurisu import Kurisu


class RuleAddition(ui.Modal, title='Rule Addition'):
    rule_number = ui.TextInput(label='Rule Number')
    rule_title = ui.TextInput(label='Title', required=False)
    rule_description = ui.TextInput(label='Description', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        bot: 'Kurisu' = interaction.client  # type: ignore
        try:
            number = int(self.rule_number.value)
        except ValueError:
            await interaction.response.send_message('Invalid rule number', ephemeral=True)
            return

        rule = bot.configuration.rules.get(number)
        if rule:
            title = self.rule_title.value if self.rule_title.value else rule.title
            description = self.rule_description.value if self.rule_description.value else rule.description
            await bot.configuration.edit_rule(number, title, description)
            await interaction.response.send_message(f"Rule {number} edited successfully!", embed=Embed(title=title, description=description, color=gen_color(number)))
        else:
            title = self.rule_title.value
            description = self.rule_description.value
            if not title or description:
                return await interaction.response.send_message("Title and description is required for new rules", ephemeral=True)
            await bot.configuration.add_rule(number, title, description)
            await interaction.response.send_message(f"Rule {number} created successfully!", embed=Embed(title=f"Rule {number} - {title}", description=description, color=gen_color(number)))
        await bot.reload_extension("cogs.rules")

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Error when creating rule', ephemeral=True)
