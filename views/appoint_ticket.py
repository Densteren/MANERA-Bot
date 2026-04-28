# views/take_ticket.py
import discord
from views.close_ticket import CompleteButton
from config import STAFF, RENDERMAKER_ROLE
ASSIGN_CACHE = {}

class AppointTicketButton(discord.ui.Button):
    def __init__(self): super().__init__(label="Назначить рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint", emoji="🪪")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        role = interaction.guild.get_role(RENDERMAKER_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select( placeholder="Выберите рендермейкера", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            new_view = discord.ui.View()
            new_view.add_item(CompleteButton())
            new_view.add_item(TicketTakenButton(user=member.display_name))
            await message_aptb.edit(view=new_view)
            await msd_appoint.edit(content=f"🪪 {member.mention} назначен", view=None)
            
        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        global msd_appoint
        msd_appoint = await interaction.followup.send(view=view, ephemeral=True)
    

class AssignDesiredTicketButton(discord.ui.Button):
    def __init__(self): super().__init__(label="Назначить желаемого рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired", emoji="🪪")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        user_id = ASSIGN_CACHE.get(str(interaction.channel.id))
        if not user_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(user_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)


class RenderView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
        
    @discord.ui.button(label="Назначить рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint", emoji="🪪")
    async def appoint(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        role = interaction.guild.get_role(RENDERMAKER_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select(placeholder="Выберите рендермейкера", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            new_view = discord.ui.View()
            new_view.add_item(CompleteButton())
            new_view.add_item(TicketTakenButton(user=member.display_name))
            await message_aptb.edit(view=new_view)
            await msd_appoint.edit(content=f"🪪 {member.mention} назначен", view=None)
            
        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)
        global msd_appoint
        msd_appoint = await interaction.followup.send(view=view, ephemeral=True)
    
    @discord.ui.button(label="Назначить желаемого рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired", emoji="🪪")
    async def appoint_desired(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        user_id = ASSIGN_CACHE.get(str(interaction.channel.id))
        if not user_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(user_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)


class TicketTakenButton(discord.ui.Button):
    def __init__(self, user=str): super().__init__(label=user, style=discord.ButtonStyle.gray, custom_id="ticket:taken", emoji="📝", disabled=True)
    async def callback(self): pass
