import discord, io, aiohttp
from discord import ui
from config import TICKET_CREATE_CATEGORY, GUILD_ID, RENDERMAKER_ROLE, ANIMATOR_ROLE, TITLE_ANIMATOR_ROLE
from fs import generate_random_id
from views.close_ticket import CloseButton
from views.appoint_ticket import AppointTicketButtonRender, AssignDesiredTicketButtonRender, AppointTicketButtonAnimator, AssignDesiredTicketButtonAnimator, AppointTicketButtonTitleAnimator, AssignDesiredTicketButtonTitleAnimator
from config import TICKET_VIEWIER_ROLES, STAFF
from images.images_url import CREATEREQUESTMODAL
class CreateRequestModal(discord.ui.Modal):
    def __init__(self, type: str, bot):
        super().__init__(title="Ты заказываешь в MANER`E")
        self.type = type
        self.bot = bot
        if type == "render":
            role = bot.get_guild(GUILD_ID).get_role(RENDERMAKER_ROLE)
            text_render = "Рендермейкер"
            text_models = "Файлы для рендера"
        elif type == "animation":
            role = bot.get_guild(GUILD_ID).get_role(ANIMATOR_ROLE)
            text_render = "Аниматор"
            text_models = "Файлы для анимации"
        elif type == "title":
            role = bot.get_guild(GUILD_ID).get_role(TITLE_ANIMATOR_ROLE)
            text_render = "Мультипликатор"
            text_models = "Файлы для анимации"
            
        sorted_members = sorted(role.members, key=lambda m: m.display_name.lower())
        
        self.render_select = discord.ui.Select(
            placeholder="Кого хотите видеть на месте исполнителя?",
            required=True,
            
            options=[
                discord.SelectOption(
                    label="Без разницы",
                    value="0",
                    emoji="<a:soggy_boom:1421917569954091081>",
                    default=True
                ),
                *[discord.SelectOption(
                    label=m.display_name,
                    value=str(m.id),
                    emoji="<a:shulker_ping:591776781523222549>"
                )
                for m in sorted_members[:24]
                ]
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
            text=text_render,
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
            text=text_models,
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
        selected = self.render_select.values[0] if self.render_select.values else "0"
        created = await category.create_text_channel(name=f"{self.type}-{interaction.user.name}-{ticket_id}", overwrites=overwrites, topic=f"{interaction.user.id}:{selected}", reason="БЫЛ ОТКРЫТ ТИКЕТ")
        if selected == "0": render = "Без разницы"
        else:
            member = interaction.guild.get_member(int(selected))
            render = member.display_name if member else "Не найден"
        
        await interaction.followup.send(content=f"Тикет создан: <#{created.id}>", ephemeral=True)
        view = discord.ui.View(timeout=None) 
        view.add_item(CloseButton())
        render_id = selected if selected != "0" else None
        if self.type == "render": 
            name1 = "рендермейкером"
            name2 = "Рендермейкер"
            if render_id is not None:
                user = interaction.guild.get_member(int(render_id))
                if user: view.add_item(AssignDesiredTicketButtonRender(user.display_name.lower()))
            view.add_item(AppointTicketButtonRender())
        if self.type == "animation":
            name1 = "аниматором"
            name2 = "Аниматор"
            if render_id is not None:
                user = interaction.guild.get_member(int(render_id))
                if user: view.add_item(AssignDesiredTicketButtonAnimator(user.display_name.lower()))
            view.add_item(AppointTicketButtonAnimator())
        if self.type == "title":
            name1 = "мультипликатором"
            name2 = "Мультипликатор"
            if render_id is not None:
                user = interaction.guild.get_member(int(render_id))
                if user: view.add_item(AssignDesiredTicketButtonTitleAnimator(user.display_name.lower()))
            view.add_item(AppointTicketButtonTitleAnimator())
        
        message_data = {"flags": 36864, "components": [
            {"type": 10,"content": f"Привет, <@{interaction.user.id}>! Мы скоро возьмёмся за твой заказ, а пока прочитай всю информацию ниже <:Arrow_Down_Highlighted:1488578347716972865>"},
            {"type": 17, "components": [
                {"type": 12, "items": [{"media": {"url": CREATEREQUESTMODAL}}]},
                {"type": 14, "spacing": 2, "divider": True},
                
                {"type": 10, "content": f"# <:866605190396510238:1508914561439367501> Заказ {self.type.title()} #{ticket_id}"},
                {"type": 14, "spacing": 1, "divider": True},
                {"type": 10, "content": f"<:866951385148293170:1508810624971309066> Сроки выполнения твоего заказа начинаются от 2 до 14 дней.\n\n<:866951385416859668:1508810626724790434> Стоимость заказа обговаривается с {name1} который будет работать над твоим заказом.\n\n<:866951386187825182:1508810629127995422> Перед началом выполнения заказа требуется внести предоплату в размере **100%** от всей стоимости заказа."},
                {"type": 14, "spacing": 1, "divider": True},
                
                {"type": 10, "content": f"**<:865488228387651584:1508914564312600746> ТЗ:** ```{self.task.value}```\n**<:866943907698180137:1508914567387025420> {name2}:** ```{render}```\n**<:860133545905225768:1508914562869624953> Сроки:** ```{self.time.value}```"}
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
        if discord_files: await created.send(content="### > <:Arms_Up_Pottery_Sherd:1512136849966104847> Загруженные файлы:", files=discord_files)
