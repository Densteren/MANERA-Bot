from config import TICKET_CREATE_CATEGORY, GUILD_ID
from datetime import datetime, timezone, timedelta
import random
import discord

def generate_random_id():
    now = datetime.now(timezone(timedelta(hours=3)))
    hour = now.hour
    if 2 <= hour < 6:
        shift = "01"
    elif 6 <= hour < 10:
        shift = "02"
    elif 10 <= hour < 14:
        shift = "03"
    elif 14 <= hour < 18:
        shift = "04"
    elif 18 <= hour < 22:
        shift = "05"
    else:
        shift = "06"
    date_str = now.strftime("%y%m")
    day_str = now.strftime("%d")
    rand = random.randint(1000, 9999)
    return f"{date_str}-{day_str}{shift}-{rand}"

async def get_user_tickets(guild, user):
    count = 0

    for channel in guild.text_channels:
        if channel.category_id != TICKET_CREATE_CATEGORY:
            continue

        if user.name.lower() in channel.name.lower():
            count += 1

    return count

class CloseDMView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Send from Studio`s MANERA ", style=discord.ButtonStyle.url, url=f"https://discord.com/channels/{GUILD_ID}"))
        self.add_item(HideMsgDM())
        
class HideMsgDM(discord.ui.Button):
    def __init__(self): super().__init__(style=discord.ButtonStyle.gray, custom_id="dm:hide", emoji="<:Blindness:1488848474047905892>")
    async def callback(self, interaction: discord.Interaction): await interaction.message.delete()