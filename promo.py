import discord, os, json, datetime, math, aiohttp, io
from config import STAFF, CARD, BUYER_ROLE, ID_GUILD_OWNER
from images.images_url import PAYMENT
CACHE = {}
PROMOCODES_FILE = "promocodes.json"

class PromoCodeManager:
    def __init__(self):
        if not os.path.exists(PROMOCODES_FILE):
            with open(PROMOCODES_FILE, "w", encoding="utf-8") as f: json.dump({}, f, indent=4)

    def load(self):
        with open(PROMOCODES_FILE, "r", encoding="utf-8") as f: return json.load(f)

    def save(self, data): 
        with open(PROMOCODES_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

    def create(self, code: str, type: str, value: int, min_order: int, max_uses: int, expires_at: str):
        data = self.load()
        if code in data: return False
        data[code] = {"type": type, "value": value, "min_order": min_order, "max_uses": max_uses, "expires_at": expires_at, "used_by": []}
        self.save(data)
        return True

    def delete(self, code: str):
        data = self.load()
        if code not in data: return False
        del data[code]
        self.save(data)
        return True

    def use(self, code: str, user_id: int, order_price: int):
        data = self.load()
        if code not in data: return False, None, "Промокод не существует"
        if user_id in data[code]["used_by"]: return False, None, "Вы уже использовали этот промокод"
        if data[code]["min_order"] is not None:
            if order_price < data[code]["min_order"]: return False, None, "Сумма заказа слишком мала"
        if data[code]["expires_at"] is not None:
            if datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))) > datetime.datetime.strptime(data[code]["expires_at"], "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=datetime.timezone(datetime.timedelta(hours=3))): return False, None, "Промокод истёк"
        if data[code]["max_uses"] is not None:
            if len(data[code]["used_by"]) >= data[code]["max_uses"]: return False, None, "Лимит активаций исчерпан"
            data[code]["max_uses"] -= 1
        data[code]["used_by"].append(user_id)
        self.save(data)
        return True, data[code]["type"], data[code]["value"]

    def get_all(self): return self.load()

class PayOrder(discord.ui.Button):
    def __init__(self): super().__init__(label="Потвердить оплату", style=discord.ButtonStyle.gray, custom_id="ticket:pay_order", emoji="<:Jump_Boost:1512109201902666009>")

    async def callback(self, interaction: discord.Interaction):
        cache_data = CACHE.get(interaction.channel.id)
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        if interaction.user.id != user_id and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете потвердить оплату", ephemeral=True)
        if not CACHE.get(interaction.channel.id): return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
        await interaction.response.send_modal(PayOrderModal())


class PayOrderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Потверждение оплаты")
        self.models_upload = discord.ui.FileUpload(required=True, max_values=1)
        self.models = discord.ui.Label(text="Прикрепите скриншот оплаты", component=self.models_upload)
        self.add_item(self.models)
    
    async def on_submit(self, interaction: discord.Interaction):
        cache_data = CACHE.get(interaction.channel.id)
        if not cache_data: return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
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
        await interaction.response .send_message("Оплата подтверждена!", ephemeral=True)
        if not any(role.id in STAFF for role in interaction.user.roles): await interaction.user.add_roles(interaction.guild.get_role(BUYER_ROLE), reason="ЗАКАЗ ОПЛАЧЕН")
        await interaction.channel.send(content=f"<@{cache_data['manager']}> <@{ID_GUILD_OWNER}>, заказ был оплачен!", files=discord_files)
        cache_data.pop(interaction.channel.id, None)
        await interaction.message.delete()


class UsePromo(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Использовать промо-код", style=discord.ButtonStyle.gray, custom_id="ticket:use_promo", emoji="<:Checkbox_Highlighted:1512108576884260885>")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        if interaction.user.id != user_id: return await interaction.response.send_message("Вы не можете использовать промо-код", ephemeral=True)
        if not CACHE.get(interaction.channel.id): return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
        await interaction.response.send_modal(UsePromoModal(self.bot))

async def promo_autocomplete(interaction: discord.Interaction, current: str): return [discord.app_commands.Choice(name=code, value=code) for code in PromoCodeManager().get_all().keys() if current.lower() in code.lower()][:25]

class UsePromoModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Использовать промо-код")
        self.bot = bot
        self.code = discord.ui.TextInput(label="Промо-код", placeholder="Промокод можно использовать только один раз!", required=True, max_length=25)
        self.add_item(self.code)
    
    async def on_submit(self, interaction: discord.Interaction):
        cache_data = CACHE.get(interaction.channel.id)
        if not cache_data: return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
        success, type, value = PromoCodeManager().use(self.code.value.upper(), interaction.user.id, cache_data["data"])
        if not success: return await interaction.response.send_message(f"❌ {value}", ephemeral=True)
        
        if type == "fixed":
            result = f"{value}₽"
            final_price = max(0, cache_data["data"] - value)
        elif type == "percent":
            result = f"{value}%"
            final_price = max(0, math.ceil(cache_data["data"] - cache_data["data"] * value / 100))

        new_view = discord.ui.View()
        new_view.add_item(PayOrder())
        new_view.add_item(UsedPromo(code=self.code.value.upper()))
        await interaction.message.edit(view=new_view)
        message_data = {"flags": 36864, "components": [
            {"type": 17, "components": [
                {"type": 12, "items": [{"media": {"url": PAYMENT}}]},
                {"type": 14, "spacing": 2, "divider": True},
                {"type": 10, "content": f"# <:866599434375528488:1508904126082187576> Оплата заказа\n### > Карта:\n{CARD}\n\n### > Сумма к оплате:\n~~*{cache_data["data"]}*~~** {final_price}**₽\n-# использован промо-код {self.code.value.upper()} на {result} скидку\n\n### > Инструкция по оплате:\n1. Отправьте сумму на карту, указанную выше с комментарием «`Оплата заказа: {interaction.channel.name}`».\n2. После отправки средств нажмите на кнопку «Подтвердить оплату» и прикрепите скриншот с переводом в открывшемся окне. "}
            ]}
        ]}
  
        await self.bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=interaction.channel.id, message_id=cache_data["message_id"]), json=message_data)
        await interaction.response.send_message(f"✅ Вы активировали промокод на скидку {result}", ephemeral=True)
        

class PayView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Потвердить оплату", style=discord.ButtonStyle.gray, custom_id="ticket:pay_order", emoji="<:Jump_Boost:1512109201902666009>")
    async def pay_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        if interaction.user.id != user_id and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете потвердить оплату", ephemeral=True)
        if not CACHE.get(interaction.channel.id): return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
        await interaction.response.send_modal(UsePromoModal(self.bot))
    
    @discord.ui.button(label="Использовать промо-код", style=discord.ButtonStyle.gray, custom_id="ticket:use_promo", emoji="<:Checkbox_Highlighted:1512108576884260885>")
    async def use_promo(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id, selected_id = map(int, interaction.channel.topic.split(":"))
        if interaction.user.id != user_id: return await interaction.followup.send("Вы не можете использовать промо-код", ephemeral=True)
        if not CACHE.get(interaction.channel.id): return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
        await interaction.response.send_modal(UsePromoModal(self.bot))

class UsedPromo(discord.ui.Button):
    def __init__(self, code=str): super().__init__(label=code, style=discord.ButtonStyle.gray, custom_id="ticket:used_promo", emoji="<:Checkbox_Selected_Highlighted:1512108575101816853>", disabled=True)
    async def callback(self): pass
