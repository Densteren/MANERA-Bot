import discord
import time
from fs import get_user_tickets
from config import STAFF, PLACING_AN_ORDER_CHANNEL_ID, PLACING_AN_ORDER_MESSAGE_ID, ID_GUILD_OWNER
from images.images_url import PLACING_AN_ORDER_PANEL
from modals.req import CreateRequestModal
from modals.rev import ReviewModal, CACHE, clear_old_cache
class TicketTypeSelect(discord.ui.View):
  def __init__(self, bot):
    super().__init__(timeout=None)
    self.bot = bot
    self.clear_cooldowns = {} 

  @discord.ui.select(placeholder="Выберите нужное", custom_id="ticket:placing_an_order", options=[discord.SelectOption(label="FULL RENDER", value="render", emoji="<:Netherite_Upgrade_Smithing_Templ:1495122438797660243>"), discord.SelectOption(label="CUSTOM ANIMATION", value="animation", emoji="<:Axolotl:1503669257286717440>", default=False), discord.SelectOption(label="MINECRAFT TITLE ANIMATION", value="title", emoji="<:Cherry_Hanging_Sign:1506355717303701587>", default=False)])
  async def placing_select(self, interaction: discord.Interaction, select: discord.ui.Select):
    if await get_user_tickets(interaction.guild, interaction.user) >= 2: return await interaction.response.send_message("❌ У тебя уже 2 активных тикета.", ephemeral=True)
    await interaction.response.send_modal(CreateRequestModal(select.values[0], self.bot))
    
  @discord.ui.button(label="Написать отзыв", custom_id="ticket_button:review", style=discord.ButtonStyle.gray, emoji="<:Paper:1506354283853910159>",)
  async def review_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    clear_old_cache()
    cache_data = CACHE.get(interaction.channel.id)
    if not cache_data: return await interaction.response.send_message("Кэш не найден :(", ephemeral=True)
    await interaction.response.send_modal(ReviewModal(self.bot, channel=interaction.channel.id))

  @discord.ui.button(label="Очистить выбор", custom_id="ticket:clear", style=discord.ButtonStyle.gray, emoji="<:Wind_Charged:1488847018930737262>")
  async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer(ephemeral=True)
    if time.time() - self.clear_cooldowns.get(interaction.user.id, 0) < 30 and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send(f"⏳ Подожди {int(30 - (time.time() - self.clear_cooldowns.get(interaction.user.id, 0)))} сек.", ephemeral=True)
    self.clear_cooldowns[interaction.user.id] = time.time()
        
    message_data = {"flags": 36864, "components": [
      {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": PLACING_AN_ORDER_PANEL}}]},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# Оформление заказа"},
        {"type": 10, "content": "Заказывай в MANER`E\nМы создадим рендер по твоему тех-заданию в наилучшем виде и реализации."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 1, "components": [{"type": 3, "custom_id": "ticket:placing_an_order", "placeholder": "Выберите нужное", "max_values": 1, "options": [{"label": "FULL RENDER", "value": "render", "emoji": {"name": "Netherite_Upgrade_Smithing_Templ", "id": 1495122438797660243}, "default": False}, {"label": "MINECRAFT TITLE ANIMATION", "value": "title", "emoji": {"name": "Cherry_Hanging_Sign", "id": 1506355717303701587}, "default": False}, {"label": "CUSTOM ANIMATION", "value": "animation", "emoji": {"name": "Axolotl", "id": 1503669257286717440}, "default": False}]}]},
        {"type": 1, "components": [{"type": 2, "style": 2, "label": "Очистить выбор", "emoji": {"name": "Wind_Charged", "id": 1488847018930737262},"custom_id": "ticket:clear"}]},
        {"type": 14, "spacing": 1, "divider": True},
        
        {"type": 10, "content": F"-# По всем вопросам обращаться к <@{ID_GUILD_OWNER}> или [клик](<https://discord.com/users/{ID_GUILD_OWNER}>)"}
      ]}
    ]}
        
    await self.bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=PLACING_AN_ORDER_CHANNEL_ID, message_id=PLACING_AN_ORDER_MESSAGE_ID), json=message_data)
