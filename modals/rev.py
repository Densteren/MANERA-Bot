import discord, time, aiohttp
from discord import ui
from config import REVIEWS_CHANNEL_ID
from images.images_url import REVIEW as REVIEW1
CACHE = {}
CACHE_LIFETIME = 60 * 60 * 24 * 3

def clear_old_cache():
    expired = [key for key, value in CACHE.items() if time.time() - value["created_at"] > CACHE_LIFETIME]
    for key in expired: del CACHE[key]

class ReviewModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Оставьте пожалуйста отзыв")
        self.bot = bot
        
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
        cache_data = CACHE.get(interaction.channel.id)
        if not cache_data: return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)

        REVIEW = []
        async with aiohttp.ClientSession() as session:
            for url in [url for url in cache_data["data"] if url]:
                try:
                    async with session.head(url, allow_redirects=True) as resp:
                        content_type = resp.headers.get("Content-Type", "").lower()
                        if (content_type.startswith("image/") or content_type.startswith("video/")): REVIEW.append(url)
                except Exception: pass
        WORKER = self.bot.get_user(cache_data["worker"])
        if not WORKER:
            try: WORKER = await interaction.guild.fetch_member(cache_data["worker"])
            except Exception as e: return await interaction.response.send_message(f"Непредвиденная ошибка: {e}", ephemeral=True)
        if cache_data["worker_type"] == "rendermaker": WORKER_TYPE = "Рендерер"
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
                {"type": 12, "items": [{"media": {"url": url}} for url in REVIEW][:10]},
                {"type": 14, "spacing": 2, "divider": True},
                {"type": 10, "content": f"# <:860123643756281876:1508810637575323709> Новый отзыв\n## > Оценка:  {stars}\n### > {WORKER_TYPE}: {WORKER.mention}{critique}\n\n-# Отзыв оставил {interaction.user.mention}"}
            ]}
        ]}
  
        await self.bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=REVIEWS_CHANNEL_ID), json=message_data)
        await interaction.response.send_message("Спасибо за оставленный отзыв!", ephemeral=True)
        
        message_data1 = {"flags": 36864, "components": [
            {"type": 17, "components": [
                {"type": 12, "items": [{"media": {"url": REVIEW1}}]},
                {"type": 14, "spacing": 2, "divider": True},
                {"type": 10, "content": f"# <:859388130411282442:1508810635981361212> Отзыв о заказе\n\n### > Инструкция по написанию отзыва:\n1. Вам не нужно загружать готовый продукт, бот это сделает за вас.\n2. Вам нужно нажать на кнопку «Написать отзыв» и заполнить поля в открывшемся окне."}
            ]}
        ]}
        
        await self.bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=interaction.channel.id, message_id=interaction.message.id), json=message_data1)
        CACHE.pop(interaction.channel.id, None)
