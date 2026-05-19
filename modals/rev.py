import discord
from discord import ui
from config import REVIEWS_CHANNEL_ID
CACHE = {}

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
        REVIEW = CACHE[self.channel]
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
                {"type": 10, "content": f"# Новый отзыв\n## > Оценка:  {stars}{critique}\n-# Отзыв оставил {interaction.user.mention}"}
            ]}
        ]}
  
        await self.bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=REVIEWS_CHANNEL_ID), json=message_data)
        await interaction.response.send_message("Спасибо за оставленный отзыв!", ephemeral=True)
        CACHE.pop(self.channel, None)
