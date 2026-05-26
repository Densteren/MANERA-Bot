import discord, time
from discord import ui
from config import REVIEWS_CHANNEL_ID
CACHE = {}
CACHE_LIFETIME = 60 * 60 * 24 * 3

def clear_old_cache():
    expired = [key for key, value in CACHE.items() if time.time() - value["created_at"] > CACHE_LIFETIME]
    for key in expired: del CACHE[key]

class ReviewModal(discord.ui.Modal):
    def __init__(self, bot, channel):
        super().__init__(title="Оставьте пожалуйста отзыв")
        self.bot = bot
        self.channel = channel
        
        self.review_select = discord.ui.Select(placeholder="Оцените наш сервис", required=True,
            options=[
                discord.SelectOption(label="1 звезда", value="1", emoji="<:glow:1488864058500448306>"),
                discord.SelectOption(label="2 звезды", value="2", emoji="<:glow:1488864058500448306>"),
                discord.SelectOption(label="3 звезды", value="3", emoji="<:glow:1488864058500448306>"),
                discord.SelectOption(label="4 звезды", value="4", emoji="<:glow:1488864058500448306>"),
                discord.SelectOption(label="5 звёзд", value="5", emoji="<:glow:1488864058500448306>")
            ]
        )
        self.review_selected = ui.Label(text="Колличество звёзд", component=self.review_select)
        
        self.review_text = discord.ui.TextInput(label="Рецензия", required=False, style=discord.TextStyle.paragraph, max_length=1500, placeholder="Вы можете написать рецензию о нашем сервисе.\nВаше мнение очень важно для нас!")
        
        
        self.add_item(self.review_selected)
        self.add_item(self.review_text)

    async def on_submit(self, interaction: discord.Interaction):
        cache_data = CACHE.get(self.channel)
        if not cache_data: return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)

        REVIEW = cache_data["data"]
        WORKER = self.bot.get_user(cache_data["worker"])
        if not WORKER:
            try: WORKER = await interaction.guild.fetch_member(cache_data["worker"])
            except Exception as e: return await interaction.response.send_message(f"Непредвиденная ошибка: {e}", ephemeral=True)
        if cache_data["worker_type"] == "renderer": WORKER_TYPE = "Рендерер"
        elif cache_data["worker_type"] == "title_animator": WORKER_TYPE = "Мультипликатор"
        elif cache_data["worker_type"] == "animator": WORKER_TYPE = "Аниматор"
                
        critique = ""
        if self.review_text.value: critique = f"\n\n## > Рецензия:\n{self.review_text.value}"
        stars = "Ошибка"
        if self.review_select.values[0] == "1": stars = "<:glow:1488864058500448306>"
        elif self.review_select.values[0] == "2": stars = "<:glow:1488864058500448306> <:glow:1488864058500448306>"
        elif self.review_select.values[0] == "3": stars = "<:glow:1488864058500448306> <:glow:1488864058500448306> <:glow:1488864058500448306>"
        elif self.review_select.values[0] == "4": stars = "<:glow:1488864058500448306> <:glow:1488864058500448306> <:glow:1488864058500448306> <:glow:1488864058500448306>"
        elif self.review_select.values[0] == "5": stars = "<:glow:1488864058500448306> <:glow:1488864058500448306> <:glow:1488864058500448306> <:glow:1488864058500448306> <:glow:1488864058500448306>"
        
        message_data = {"flags": 36864, "components": [
            {"type": 17, "components": [
                {"type": 12, "items": [{"media": {"url": REVIEW}}]},
                {"type": 14, "spacing": 2, "divider": True},
                {"type": 10, "content": f"# <:860123643756281876:1508810637575323709> Новый отзыв\n## > Оценка:  {stars}\n### > {WORKER_TYPE}: {WORKER.mention}{critique}\n\n-# Отзыв оставил {interaction.user.mention}"}
            ]}
        ]}
  
        await self.bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=REVIEWS_CHANNEL_ID), json=message_data)
        await interaction.response.send_message("Спасибо за оставленный отзыв!", ephemeral=True)
        CACHE.pop(self.channel, None)
