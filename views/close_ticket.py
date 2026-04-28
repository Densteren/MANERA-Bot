import discord
from asyncio import sleep
from config import TICKET_VIEWIER_ROLES, STAFF, BUYER_ROLE, TICKET_CLOSE_CATEGORY

class CloseButton(discord.ui.Button):
    def __init__(self): super().__init__(label="Отменить заказ", style=discord.ButtonStyle.red, custom_id="ticket:close", emoji="🔒")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id != int(interaction.channel.topic) and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете закрыть чужой заказ", ephemeral=True)
        global msg_close
        msg_close = await interaction.followup.send("Ты уверен, что хочешь оборвать фотоплёнку?", view=ConfirmCloseView(interaction.message), ephemeral=True)

class CompleteButton(discord.ui.Button):
    def __init__(self): super().__init__(label="Завершить заказ", style=discord.ButtonStyle.green, custom_id="ticket:complete", emoji="🔒")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете завершить заказ", ephemeral=True)
        global msg_complite
        msg_complite = await interaction.followup.send("Ты уверен, что хочешь отложить фотоплёнку?", view=ConfirmCompleteView(interaction.message), ephemeral=True)


class ConfirmCompleteView(discord.ui.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=None)
        self.message = message

    @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.danger, custom_id="ticket:complete:confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(int(interaction.channel.topic))
        await interaction.channel.send(f"{member.mention}, {interaction.user.mention} сохранил твою фотоплёнку. *Надеемся увидеть тебя еще раз!*")
        await msg_complite.edit(content=f"Тикет закрыт!", view=None)
        await self.message.delete()
        await sleep(3)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False)}
        for role_id in TICKET_VIEWIER_ROLES:
            role = interaction.guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)
        for role_id in STAFF:
            role = interaction.guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)
        old_name = interaction.channel.name
        category = interaction.guild.get_channel(TICKET_CLOSE_CATEGORY)
        if not category: category = None
        await interaction.channel.edit(overwrites=overwrites, name=f"closed-{old_name}", category=category, reason="ТИКЕТ БЫЛ ЗАКРЫТ")
        await member.remove_roles(interaction.guild.get_role(BUYER_ROLE), reason="ТИКЕТ БЫЛ ЗАКРЫТ")

    @discord.ui.button(label="Отмена", style=discord.ButtonStyle.secondary, custom_id="ticket:complete:reject")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await msg_complite.edit(content="Закрытие отменено — вы передумали.", view=None)

class ConfirmCloseView(discord.ui.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=None)
        self.message = message

    @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.danger, custom_id="ticket:close:confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(int(interaction.channel.topic))
        if interaction.user.id != int(interaction.channel.topic):
            await interaction.channel.send(f"{member.mention}, {interaction.user.mention} оборвал твою фотоплёнку. *Надеемся увидеть тебя еще раз!*")
            await msg_close.edit(content="Тикет закрыт!", view=None)
        else:
            await interaction.channel.send(f"{member.mention} оборвал фотоплёнку. *Надеемся увидеть тебя еще раз!*")
            await msg_close.edit(content="Тикет закрыт!\n*Надеемся увидеть тебя еще раз!*", view=None)
        await self.message.delete()
        await sleep(3)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False)}
        for role_id in TICKET_VIEWIER_ROLES:
            role = interaction.guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)
        for role_id in STAFF:
            role = interaction.guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)
        old_name = interaction.channel.name
        category = interaction.guild.get_channel(TICKET_CLOSE_CATEGORY)
        if not category: category = None
        await interaction.channel.edit(overwrites=overwrites, name=f"closed-{old_name}", category=category, reason="ТИКЕТ БЫЛ ЗАКРЫТ")
        await member.remove_roles(interaction.guild.get_role(BUYER_ROLE), reason="ТИКЕТ БЫЛ ЗАКРЫТ")


    @discord.ui.button(label="Отмена", style=discord.ButtonStyle.secondary, custom_id="ticket:close:reject")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await msg_close.edit(content="Закрытие отменено — вы передумали.", view=None)

    
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Отменить заказ", style=discord.ButtonStyle.red, custom_id="ticket:close", emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id != int(interaction.channel.topic) and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете закрыть чужой заказ", ephemeral=True)
        global msg_close
        msg_close = await interaction.followup.send("Ты уверен, что хочешь оборвать фотоплёнку?",view=ConfirmCloseView(interaction.message), ephemeral=True)
    
    @discord.ui.button(label="Завершить заказ", style=discord.ButtonStyle.green, custom_id="ticket:complete", emoji="🔒")
    async def complete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете завершить заказ", ephemeral=True)
        global msg_complite
        msg_complite = await interaction.followup.send("Ты уверен, что хочешь отложить фотоплёнку?", view=ConfirmCompleteView(interaction.message), ephemeral=True)
        