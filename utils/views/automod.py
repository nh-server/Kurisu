import datetime
from typing import Optional

import discord
from discord import (Interaction, AutoModRuleTriggerType, AutoModRule, AutoModRuleActionType, ButtonStyle,
                     AutoModRuleAction, TextStyle, Embed)
from discord.ui import Select, Modal, TextInput

from utils.utils import text_to_discord_file, gen_color, parse_time
from utils.views.base import BaseView


class TimeoutInput(Modal):
    duration = TextInput(label='Timeout duration (0s for disabling)', style=TextStyle.short,
                         required=True, placeholder="Time in #d#h#m#s format.")

    def __init__(self, automod_rule: AutoModRule):
        super().__init__(title='Timeout Update')
        self.automod_rule = automod_rule

    async def on_submit(self, interaction: Interaction):
        secs = parse_time(self.duration.value)
        if secs == -1:
            await interaction.response.send_message('Invalid time format', ephemeral=True)
        elif secs > 2419200:
            await interaction.response.send_message('Timeouts can\'t be longer than 28 days.', ephemeral=True)
        elif secs > 0:
            action: Optional[AutoModRuleAction] = discord.utils.get(self.automod_rule.actions,
                                                                    type=AutoModRuleActionType.timeout)
            delta = datetime.timedelta(seconds=secs)
            if action:
                action.duration = delta
                await self.automod_rule.edit(actions=self.automod_rule.actions)
            else:
                new_action = AutoModRuleAction(duration=delta)
                self.automod_rule.actions.append(new_action)
                await self.automod_rule.edit(actions=self.automod_rule.actions)
            await interaction.response.send_message('Timeout updated succesfully. Refresh the view.', ephemeral=True)
        elif secs == 0:
            action: Optional[AutoModRuleAction] = discord.utils.get(self.automod_rule.actions,
                                                                    type=AutoModRuleActionType.timeout)
            if action:
                self.automod_rule.actions.remove(action)
                await self.automod_rule.edit(actions=self.automod_rule.actions)
            await interaction.response.send_message('Timeout removed succesfully. Refresh the view.', ephemeral=True)


class AutoModRulesView(BaseView):
    def __init__(self, automod_rules: list[AutoModRule], author: discord.Member):
        super().__init__(author=author)
        self.selected: Optional[AutoModRule] = None
        self.add_item(AutoModRuleSelect(automod_rules))
        self.embed_colour = gen_color(author.id)
        self.default_embed = Embed(title="AutoMod Rules", description="Select an AutoMod Rule",
                                   colour=self.embed_colour)

    @discord.ui.button(label="General", style=ButtonStyle.secondary, disabled=True)
    async def general_information(self, interaction: Interaction, button: discord.ui.Button):
        embed = self.create_rule_embed()
        self.set_timeout.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Actions", style=ButtonStyle.secondary, disabled=True)
    async def actions_information(self, interaction: Interaction, button: discord.ui.Button):
        assert self.selected is not None
        embed = self.create_actions_embed()
        if self.selected.trigger.type not in (AutoModRuleTriggerType.keyword_preset, AutoModRuleTriggerType.spam):
            self.set_timeout.disabled = False
        self.general_information.disabled = False
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Set timeout", style=ButtonStyle.secondary, disabled=True)
    async def set_timeout(self, interaction: Interaction, button: discord.ui.Button):
        assert self.selected is not None
        await interaction.response.send_modal(TimeoutInput(self.selected))

    @discord.ui.button(label="Export keywords", style=ButtonStyle.secondary, disabled=True)
    async def export_keywords(self, interaction: Interaction, button: discord.ui.Button):
        assert self.selected is not None
        text = '\n'.join(self.selected.trigger.keyword_filter)
        file = text_to_discord_file(text, name='export.txt')
        await interaction.response.send_message(file=file, ephemeral=True)

    @discord.ui.button(label="Stop", style=ButtonStyle.red, disabled=False, row=0)
    async def stop_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        self.stop()

    def create_rule_embed(self) -> Embed:
        assert self.selected is not None
        embed = Embed(title=f"{self.selected.name} Rule", colour=self.embed_colour)
        embed.add_field(name="Enabled", value=self.selected.enabled)
        embed.add_field(name="Creator", value=self.selected.creator)
        trigger_type = self.selected.trigger.type
        embed.add_field(name="Trigger", value=trigger_type.name)
        if trigger_type is AutoModRuleTriggerType.keyword:
            embed.add_field(name="Keywords", value=len(self.selected.trigger.keyword_filter))
            embed.add_field(name="Regex patts", value=len(self.selected.trigger.regex_patterns))
        elif trigger_type is AutoModRuleTriggerType.mention_spam:
            embed.add_field(name="Mention limit", value=self.selected.trigger.mention_limit)
        elif trigger_type is AutoModRuleTriggerType.keyword_preset:
            presets = ['profanity', 'sexual_content', 'slurs']
            embed.add_field(name="Presets", value=' '.join(
                preset for preset in presets if getattr(self.selected.trigger.presets, preset)))
        return embed

    def create_actions_embed(self):
        assert self.selected is not None
        embed = Embed(title=f"{self.selected.name} Trigger", colour=self.embed_colour)
        embed.add_field(name="Actions", value=' '.join(f'`{action.type.name}`' for action in self.selected.actions))
        if alert_action := discord.utils.get(self.selected.actions, type=AutoModRuleActionType.send_alert_message):
            embed.add_field(name="Alert Channel", value=f"<#{alert_action.channel_id}>")
        if timeout_action := discord.utils.get(self.selected.actions, type=AutoModRuleActionType.timeout):
            embed.add_field(name="Timeout Duration", value=str(timeout_action.duration))
        return embed


class AutoModRuleSelect(Select['AutoModRulesView']):

    def __init__(self, automod_rules: list[AutoModRule]):
        super().__init__(placeholder="Select an AutoMod rule.")
        self.rules: dict = {r.name: r for r in automod_rules}
        self.populate()

    def populate(self):
        for rule in self.rules.values():
            self.add_option(label=rule.name, value=rule.name, description="Enabled" if rule.enabled else "Disabled")

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        self.view.selected = self.rules[self.values[0]]
        self.view.set_timeout.disabled = True
        if self.view.selected:
            self.view.actions_information.disabled = False
            self.view.export_keywords.disabled = self.view.selected.trigger.type is not AutoModRuleTriggerType.keyword
            embed = self.view.create_rule_embed()
        else:
            embed = self.view.default_embed
        await interaction.response.edit_message(view=self.view, embed=embed)
