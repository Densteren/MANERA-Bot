# views/take_ticket.py
import discord
from views.close_ticket import CompleteButton
from config import STAFF, RENDERMAKER_ROLE, ANIMATOR_ROLE, TITLE_ANIMATOR_ROLE

class AppointTicketButtonRender(discord.ui.Button):
    def __init__(self): super().__init__(label="Назначить рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_render", emoji="<:Luck:1508919286096461916>")

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
            user_id, selected_id = map(int, interaction.channel.topic.split(":"))
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
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
    

class AssignDesiredTicketButtonRender(discord.ui.Button):
    def __init__(self, user): super().__init__(label=f"Назначить {user}", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired_render", emoji="<:Luck:1508919286096461916>")

    async def callback(self, interaction: discord.Interaction):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        if not selected_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(selected_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)



class AppointTicketButtonAnimator(discord.ui.Button):
    def __init__(self): super().__init__(label="Назначить аниматора", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_animator", emoji="<:Luck:1508919286096461916>")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить аниматора", ephemeral=True)
        role = interaction.guild.get_role(ANIMATOR_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select( placeholder="Выберите аниматора", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            user_id, selected_id = map(int, interaction.channel.topic.split(":"))
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
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
    

class AssignDesiredTicketButtonAnimator(discord.ui.Button):
    def __init__(self, user): super().__init__(label=f"Назначить {user}", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired_animator", emoji="<:Luck:1508919286096461916>")

    async def callback(self, interaction: discord.Interaction):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить аниматора", ephemeral=True)
        if not selected_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(selected_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)



class AppointTicketButtonTitleAnimator(discord.ui.Button):
    def __init__(self): super().__init__(label="Назначить мультипликатора", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_title_animator", emoji="<:Luck:1508919286096461916>")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить мультипликатора", ephemeral=True)
        role = interaction.guild.get_role(TITLE_ANIMATOR_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select( placeholder="Выберите мультипликатора", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            user_id, selected_id = map(int, interaction.channel.topic.split(":"))
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
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
    

class AssignDesiredTicketButtonTitleAnimator(discord.ui.Button):
    def __init__(self, user): super().__init__(label=f"Назначить {user}", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired_title_animator", emoji="<:Luck:1508919286096461916>")

    async def callback(self, interaction: discord.Interaction):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить мультипликатора", ephemeral=True)
        if not selected_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(selected_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)




class RenderView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
        
    @discord.ui.button(label="Назначить рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_render", emoji="<:Luck:1508919286096461916>")
    async def appoint_render(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        role = interaction.guild.get_role(RENDERMAKER_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select(placeholder="Выберите рендермейкера", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            user_id, selected_id = map(int, interaction.channel.topic.split(":"))
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
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
    
    @discord.ui.button(label="Назначить желаемого рендермейкера", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired_render", emoji="<:Luck:1508919286096461916>")
    async def appoint_desired_render(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить рендермейкера", ephemeral=True)
        if not selected_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(selected_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ РЕНДЕРМЕЙКЕРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)

    @discord.ui.button(label="Назначить аниматора", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_animator", emoji="<:Luck:1508919286096461916>")
    async def appoint_animator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить аниматора", ephemeral=True)
        role = interaction.guild.get_role(ANIMATOR_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select(placeholder="Выберите аниматора", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            user_id, selected_id = map(int, interaction.channel.topic.split(":"))
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
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
    
    @discord.ui.button(label="Назначить желаемого аниматора", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired_animator", emoji="<:Luck:1508919286096461916>")
    async def appoint_desired_animator(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить аниматора", ephemeral=True)
        if not selected_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(selected_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ АНИМАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)

    @discord.ui.button(label="Назначить мультипликатора", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_title_animator", emoji="<:Luck:1508919286096461916>")
    async def appoint_title_animator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете назначить мультипликатора", ephemeral=True)
        role = interaction.guild.get_role(TITLE_ANIMATOR_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        select = discord.ui.Select(placeholder="Выберите мультипликатора", options=[discord.SelectOption(label=m.display_name, value=str(m.id)) for m in sorted_members[:24]])
        global message_aptb
        message_aptb = interaction.message
        
        async def select_callback(interaction2: discord.Interaction):
            user_id, selected_id = map(int, interaction.channel.topic.split(":"))
            await interaction2.response.defer(ephemeral=True)
            member = interaction.guild.get_member(int(select.values[0]))
            if not member: return await interaction2.followup.send("Не найден пользователь", ephemeral=True)
            await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
            await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
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
    
    @discord.ui.button(label="Назначить желаемого мультипликатора", style=discord.ButtonStyle.gray, custom_id="ticket:appoint_desired_title_animator", emoji="<:Luck:1508919286096461916>")
    async def appoint_desired_title_animator(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        await interaction.response.defer(ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): return interaction.followup.send("Вы не можете назначить мультипликатора", ephemeral=True)
        if not selected_id: return await interaction.followup.send("Нет данных", ephemeral=True)
        member = interaction.guild.get_member(int(selected_id))
        if not member: return await interaction.followup.send("Не найден пользователь", ephemeral=True)
        await interaction.channel.set_permissions(member, view_channel=True, reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        await interaction.channel.edit(topic=f"{user_id}", reason=f"ПОДКЮЧЕНИЕ МУЛЬТИПЛИКАТОРА К ЗАКАЗУ ПО ЗАПРОСУ {interaction.user.name}")
        new_view = discord.ui.View()
        new_view.add_item(CompleteButton())
        new_view.add_item(TicketTakenButton(user=member.display_name))
        await interaction.message.edit(view=new_view)
        await interaction.followup.send(f"{member.mention} назначен", ephemeral=True)


class TicketTakenButton(discord.ui.Button):
    def __init__(self, user=str): super().__init__(label=user, style=discord.ButtonStyle.gray, custom_id="ticket:taken", emoji="<:Luck:1508919286096461916>", disabled=True)
    async def callback(self): pass
