import discord, io, aiohttp
from discord import ui
from config import TICKET_CREATE_CATEGORY, GUILD_ID, RENDERMAKER_ROLE
from fs import generate_random_id
from views.close_ticket import CloseButton
from views.appoint_ticket import AppointTicketButton, AssignDesiredTicketButton, ASSIGN_CACHE
from config import TICKET_VIEWIER_ROLES, STAFF, BUYER_ROLE
from images.images_url import CREATEREQUESTMODAL
class CreateRequestModal(discord.ui.Modal):
    def __init__(self, type: str, bot):
        super().__init__(title="Ты заказываешь в MANER`E")
        self.type = type
        self.bot = bot
        role = bot.get_guild(GUILD_ID).get_role(RENDERMAKER_ROLE)
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        
        self.render_select = discord.ui.Select(
            placeholder="Кого хотите видеть на месте рендермейкера",
            required=True,
            
            options=[
                *[discord.SelectOption(
                    label=m.display_name,
                    value=str(m.id),
                    emoji="<a:shulker_ping:591776781523222549>"
                )
                for m in sorted_members[:24]
                ],
                discord.SelectOption(
                    label="Без разницы",
                    value="any",
                    emoji="<a:soggy_boom:1421917569954091081>",
                    default=True
                )
            ]
        )
        self.models_upload = discord.ui.FileUpload(required=False, max_values=10)
        
        self.task = discord.ui.TextInput(
            label="ТЗ",
            style=discord.TextStyle.paragraph,
            max_length=1500,
            placeholder="Введи сюда своё тех-задание",
            required=True
        )
        
        self.render = ui.Label(
            text="Рендермейкер",
            component=self.render_select
        )
        
        self.time = discord.ui.TextInput(
            label="Сроки выполнения заказа",
            style=discord.TextStyle.short,
            max_length=40,
            placeholder="Желаемые сроки выполнения заказа (от 2 до 14 дней)",
            required=True,
            default="14 дней"
        )
    
        self.models = ui.Label(
            text="Файлы для рендера",
            component=self.models_upload
        )
        self.add_item(self.task)
        self.add_item(self.render)
        self.add_item(self.time)
        self.add_item(self.models)
            
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True),  }
        for role_id in TICKET_VIEWIER_ROLES:
            role = interaction.guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)
        for role_id in STAFF:
            role = interaction.guild.get_role(role_id)
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True)
        ticket_id = generate_random_id()
        category = interaction.guild.get_channel(TICKET_CREATE_CATEGORY)  
        if not category: category = None
        created = await category.create_text_channel(name=f"{self.type}-{interaction.user.name}-{ticket_id}", overwrites=overwrites, topic=f"{interaction.user.id}", reason="БЫЛ ОТКРЫТ ТИКЕТ")
        selected = self.render_select.values[0] if self.render_select.values else "any"
        if selected == "any": render = "Без разницы"
        else:
            member = interaction.guild.get_member(int(selected))
            render = member.display_name if member else "Не найден"
            ASSIGN_CACHE[f"{created.id}"] = int(selected)
        
        await interaction.followup.send(content=f"Тикет создан: <#{created.id}>", ephemeral=True)
        view = discord.ui.View(timeout=None) 
        view.add_item(CloseButton())
        view.add_item(AppointTicketButton())
        render_id = selected if selected != "any" else None
        if render_id: view.add_item(AssignDesiredTicketButton())
        
        message_data = {"flags": 36864, "components": [
            {"type": 10,"content": f"Привет, <@{interaction.user.id}>! Мы скоро возьмёмся за твой заказ, а пока прочитай всю информацию ниже <:Arrow_Down_Highlighted:1488578347716972865>"},
            {"type": 17, "components": [
                {"type": 12, "items": [{"media": {"url": CREATEREQUESTMODAL}}]},
                {"type": 14, "spacing": 2, "divider": True},
                
                {"type": 10, "content": f"# 💳 Заказ {self.type.title()} #{ticket_id}"},
                {"type": 10, "content": "`🧩` Перед началом выполнения заказа требуется внести предоплату в размере **100%** от всей стоимости заказа.\n\n`🧩` Стоимость заказа лично обговаривается с рендермейкером который будет работать над твоим заказом.\n\n`🧩` Сроки выполнения твоего заказа начинаются от 2 *полных* дней и заканчиваются до 14 *полных* дней."},
                {"type": 14, "spacing": 1, "divider": True},
                
                {"type": 10, "content": f"**✏️ ТЗ:** ```{self.task.value}```\n**🎥 Рендермейкер:** ```{render}```\n**🗓️ Сроки:** ```{self.time.value}```"}
            ]}
        ]}

        await self.bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=created.id), json=message_data)
        await created.send(view=view, silent=True)
        data = getattr(interaction, "data", {})
        resolved = data.get("resolved", {})
        attachments = resolved.get("attachments", {})
        discord_files = []
        async with aiohttp.ClientSession() as session:
            for _, att in attachments.items():
                async with session.get(att["url"]) as resp:
                    if resp.status == 200:
                        file_bytes = await resp.read()
                        discord_files.append(discord.File(io.BytesIO(file_bytes), filename=att["filename"]))
        if discord_files: await created.send(content="### 📎 `Загруженные файлы:`", files=discord_files)
        await interaction.user.add_roles(interaction.guild.get_role(BUYER_ROLE), reason="БЫЛ ОТКРЫТ ТИКЕТ")