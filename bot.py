import discord, asyncio, time
from discord.ext import commands
from discord import app_commands
from views.close_ticket import CloseView
from views.select_ticket_type import TicketTypeSelect
from views.appoint_ticket import RenderView
from modals.rev import CACHE as review_cache, clear_old_cache
from config import GUILD_ID, MEMBER_ROLE, STAFF, WORKERS, ID_GUILD_OWNER, RENDERMAKER_FORUM_ID, TICKET_CREATE_CATEGORY, CARD, INVITE, INFO_CHANNEL_ID, INFO_MESSAGE_ID, CONDITIONS_CHANNEL_ID, CONDITIONS_MESSAGE_ID, PLACING_AN_ORDER_CHANNEL_ID, PLACING_AN_ORDER_MESSAGE_ID, CATALOG_CHANNEL_ID, CATALOG_MESSAGE_ID
from images.images_url import REVIEW, PAYMENT, INFO_PANEL, CONDITIONS_PANEL, PLACING_AN_ORDER_PANEL, CATALOG_PANEL, FULL_RENDER, MINECRAFT_TITLE_ANIMATION, CUSTOM_ANIMATION, CREATEREQUESTMODAL
from fs import CloseDMView
from promo import PayView, PayOrder, UsePromo, CACHE as payment_cache, PromoCodeManager
bot = commands.Bot(command_prefix="251611!", intents=discord.Intents.all())
semaphore = asyncio.Semaphore(50)

@bot.event
async def on_ready():
  print(f"[DEBUG] {bot.user} готов!")
  await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.streaming, name=f"⟯› made by desteren ‹⟮"))
  
  bot.add_view(TicketTypeSelect(bot))
  bot.add_view(CloseView())
  bot.add_view(RenderView())
  bot.add_view(PayView(bot))
  bot.add_view(CloseDMView())
  try:
      #bot.tree.clear_commands(guild=None)
      synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))            
      print(f"[DEBUG] Изменения применены. {len(synced)}")
  except Exception as e: print(f"[DEBUG] Ошибка при синхронизации команд: {e}")

@bot.event
async def on_member_join(member: discord.Member):
  if member.guild.id != GUILD_ID: return
  await member.add_roles(member.guild.get_role(MEMBER_ROLE), reason=f"НОВЫЙ ПОЛЬЗОВАТЕЛЬ")
  #await member.send("Привет", view=CloseDMView)

@bot.event
async def on_interaction(interaction: discord.Interaction):
  async with semaphore: pass

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound): return


async def promo_autocomplete(interaction: discord.Interaction, current: str): return [app_commands.Choice(name=code, value=code) for code in PromoCodeManager().get_all().keys() if current.lower() in code.lower()][:25]

class PromoCommands(app_commands.Group):
  def __init__(self): super().__init__(name="promo-code", description="команды для работы с промо-кодами")
  
  @app_commands.command(name="create", description="создать промо-код")
  @app_commands.describe(code="Код промокода", type="Тип промокода", value="Значение скидки (процент или фиксированная сумма)", min_order="Минимальная сумма заказа для активации промокода", max_uses="Максимальное количество использований промокода", expires_at="Дата истечения срока действия промокода (в формате ГГГГ-ММ-ДД)")
  @app_commands.choices(type=[app_commands.Choice(name="Проценты", value="percent"), app_commands.Choice(name="Фиксированная сумма", value="fixed")])
  async def promo_create(self, interaction: discord.Interaction, code: str, type: app_commands.Choice[str], value: int, min_order: int = None, max_uses: int = None, expires_at: str = None):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    if PromoCodeManager().create(code.upper(), type.value, value, min_order, max_uses, expires_at): message_data = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": "### `Промо-код создан` ✅\n> * Посмотреть подробности можно с помощью команды `/promo list`"}]}]}}
    else: message_data = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": "### `Этот промо-код уже существует` ❌\n> * Посмотреть все промо-коды можно с помощью команды `/promo list`"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data)
    
  @app_commands.command(name="list", description="список промо-кодов")
  @app_commands.describe()
  async def promo_list(self, interaction: discord.Interaction):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    promos = PromoCodeManager().get_all()
    if not promos: message_data = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": "### `Промо-кодов нет` 💔\n> * Создайте новый промо-код с помощью команды `/promo create`"}]}]}}
    else: message_data = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": "\n\n".join(f"### `{code}`\n> * тип: {'проценты' if data['type'] == 'percent' else 'фиксированная сумма'}\n> * значение скидки: {data['value']}{'%' if data['type'] == 'percent' else '₽'}\n> * минимальная сумма заказа: {data['min_order'] if data['min_order'] is not None else '*отсутствует*'}\n> * использований осталось: {data['max_uses'] if data['max_uses'] is not None else '*неограничено*'}\n> * заканчивается: {f'{data['expires_at']} *(до 23:59)*' if data['expires_at'] is not None else '*бессрочно*'}\n> * использовали: {', '.join(f'<@{user_id}>' for user_id in data['used_by']) if data['used_by'] else '*никто*'}" for code, data in promos.items())}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data)
    
  @app_commands.command(name="delete", description="удалить промо-кодов")
  @app_commands.describe(code="Код промокода")
  @app_commands.autocomplete(code=promo_autocomplete)
  async def promo_delete(self, interaction: discord.Interaction, code: str):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    if PromoCodeManager().delete(code.upper()): message_data = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": "### `Промо-код удалён` ✅\n> * Создайте новый промо-код с помощью команды `/promo create`"}]}]}}
    else: message_data = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": "### `Промо-код не найден` ❌\n> * Посмотреть все промо-коды можно с помощью команды `/promo list`"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data)


class WorkersCommands(app_commands.Group):
  def __init__(self): super().__init__(name="workers", description="команды для работы с портфолио работников")
  
  @app_commands.command(name="add", description="добавить портфолио для работника")
  @app_commands.describe(user="Работник", name="Как обращаться к работнику", url="Ссылка на изображение (1 главное изображение)", price="Цена (в среднем в ₽)", catalog="Ссылка на сообщение в каталоге")
  async def worker_add(self, interaction: discord.Interaction, user: discord.Member, name: str, url: str, price: int, image1: str, image2: str, image3: str, image4: str = None, image5: str = None, image6: str = None, image7: str = None, image8: str = None, image9: str = None, video4: str = None, video5: str = None, video6: str = None, video7: str = None, video8: str = None, video9: str = None, title4: str = None, title5: str = None, title6: str = None, catalog: str = None):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)

    images = [img for img in [image1, image2, image3, image4, image5, image6, image7, image8, image9] if img]
    media_items = [{"media": {"url": img}} for img in images]
    videos = [vid for vid in [video4, video5, video6, video7, video8, video9] if vid]
    media_items2 = [{"media": {"url": vid}} for vid in videos]
    title = [vid for vid in [title4, title5, title6] if vid]
    media_items3 = [{"media": {"url": vid}} for vid in title]
    if len(images) + len(videos) + len(title) > 9: return await interaction.response.send_message(f"Максимум можно указать 9 медиафайлов. Сейчас указано: {len(images) + len(videos) + len(title)}", ephemeral=True)
    
    components = [{"type": 17, "components": [{"type": 12,"items": [{"media": {"url": url}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": (f'# {user.display_name}\nПривет! Я {user.mention}, но можно просто "**{name}**"\n\n## > Price: в среднем {price}₽')}]}, {"type": 17, "components": [{"type": 10, "content": "## > Примеры работ:"}, {"type": 12, "items": media_items}]}]
    if media_items2: components.append({"type": 17, "components": [{"type": 10, "content": "## > Примеры анимаций:"}, {"type": 12, "items": media_items2}, {"type": 10, "content": f"## > Price: смотри в {catalog if catalog else 'каталоге'}"}]})
    if media_items3: components.append({"type": 17, "components": [{"type": 10, "content": "## > Примеры тайтлов:"}, {"type": 12, "items": media_items3}, {"type": 10, "content": f"## > Price: смотри в {catalog if catalog else 'каталоге'}"}]})
    message_data = {"name": user.display_name, "message": {"flags": 36864, "components": components}}
    
    msg = await bot.http.request(discord.http.Route("POST", "/channels/{forum_id}/threads", forum_id=RENDERMAKER_FORUM_ID), json=message_data, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": CREATEREQUESTMODAL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Создано` 📝\n> * [перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{msg["id"]}/{msg["id"]}>)"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)

  @app_commands.command(name="edit", description="редактировать портфолио для работника")
  @app_commands.describe(id="ID сообщения / ветки в 📍・портфолио", user="Работник", name="Как обращаться к работнику", url="Ссылка на изображение (1 главное изображение)", price="Цена (в среднем в ₽)", catalog="Ссылка на сообщение в каталоге")
  async def worker_edit(self, interaction: discord.Interaction, id: str, user: discord.Member, name: str, url: str, price: int, image1: str, image2: str, image3: str, image4: str = None, image5: str = None, image6: str = None, image7: str = None, image8: str = None, image9: str = None, video4: str = None, video5: str = None, video6: str = None, video7: str = None, video8: str = None, video9: str = None, title4: str = None, title5: str = None, title6: str = None, catalog: str = None):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)

    images = [img for img in [image1, image2, image3, image4, image5, image6, image7, image8, image9] if img]
    media_items = [{"media": {"url": img}} for img in images]
    videos = [vid for vid in [video4, video5, video6, video7, video8, video9] if vid]
    media_items2 = [{"media": {"url": vid}} for vid in videos]
    title = [tid for tid in [title4, title5, title6] if tid]
    media_items3 = [{"media": {"url": tid}} for tid in title]
    if len(images) + len(videos) + len(title) > 9: return await interaction.response.send_message(f"Максимум можно указать 9 медиафайлов. Сейчас указано: {len(images) + len(videos) + len(title)}", ephemeral=True)
    
    components = [{"type": 17, "components": [{"type": 12,"items": [{"media": {"url": url}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": (f'# {user.display_name}\nПривет! Я {user.mention}, но можно просто "**{name}**"\n\n## > Price: в среднем {price}₽')}]}, {"type": 17, "components": [{"type": 10, "content": "## > Примеры работ:"}, {"type": 12, "items": media_items}]}]
    if media_items2: components.append({"type": 17, "components": [{"type": 10, "content": "## > Примеры анимаций:"}, {"type": 12, "items": media_items2}, {"type": 10, "content": f"## > Price: смотри в {catalog if catalog else 'каталоге'}"}]})
    if media_items3: components.append({"type": 17, "components": [{"type": 10, "content": "## > Примеры тайтлов:"}, {"type": 12, "items": media_items3}, {"type": 10, "content": f"## > Price: смотри в {catalog if catalog else 'каталоге'}"}]})
    message_data = {"flags": 36864,"components": components}
  
    thread = interaction.guild.get_channel(id)
    if thread is None:
      try: thread = await interaction.guild.fetch_channel(id)
      except Exception: return await interaction.response.send_message("Ошибка: ветка не найдена или ID неверный", ephemeral=True)
    if thread.name != user.display_name: await thread.edit(name=user.display_name, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
    await bot.http.request(discord.http.Route("PATCH", "/channels/{message_id}/messages/{message_id}", message_id=int(id)), json=message_data)
    
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": CREATEREQUESTMODAL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Изменено` ✏️\n> * [перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{int(id)}/{int(id)}>)"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)

  @app_commands.command(name="delete", description="удалить портфолио для работника")
  @app_commands.describe(id="ID сообщения / ветки в 📍・портфолио")
  async def worker_delete(self, interaction: discord.Interaction, id: str):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
  
    thread = interaction.guild.get_channel(id)
    if thread is None:
      try: thread = await interaction.guild.fetch_channel(id)
      except Exception: return await interaction.response.send_message("Ошибка: ветка не найдена или ID неверный", ephemeral=True)
    await thread.delete(reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": CREATEREQUESTMODAL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Удалено` 🗑️\n> * *портфолио удалено*"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)


@bot.tree.command(name="отзыв_review", description="показать окно отзыва", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(worker="работник, который выполнял заказ", worker_type="тип работника")
@app_commands.choices(worker_type=[app_commands.Choice(name="🎥 Рендермейкер", value="rendermaker"), app_commands.Choice(name="📸 Мультипликатор", value="title_animator"), app_commands.Choice(name="🎞️ Аниматор", value="animator")])
async def review(interaction: discord.Interaction, media: str, worker: discord.Member, worker_type: app_commands.Choice[str], media1: str = None, media2: str = None, media3: str = None, media4: str = None, media5: str = None, media6: str = None, media7: str = None, media8: str = None, media9: str = None):
  if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
  if not interaction.channel.category or interaction.channel.category.id != TICKET_CREATE_CATEGORY: return await interaction.response.send_message("Вы не можете показывать отзыв вне тикетов", ephemeral=True)
  review_cache[interaction.channel.id] = {"data": [media, media1, media2, media3, media4, media5, media6, media7, media8, media9], "worker": worker.id, "worker_type": worker_type.value, "created_at": time.time()}
    
  message_data = {"flags": 36864, "components": [
    {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": REVIEW}}]},
        {"type": 14, "spacing": 2, "divider": True},
        {"type": 10, "content": f"# <:859388130411282442:1508810635981361212> Отзыв о заказе\n\n### > Инструкция по написанию отзыва:\n1. Вам не нужно загружать готовый продукт, бот это сделает за вас.\n2. Вам нужно нажать на кнопку «Написать отзыв» и заполнить поля в открывшемся окне."},
        {"type": 1, "components": [{"type": 2, "style": 2, "label": "Написать отзыв", "emoji": {"name": "Paper", "id": 1506354283853910159}, "custom_id": f"ticket_button:review"}]}
    ]}
  ]}
  
  await bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=interaction.channel.id), json=message_data)
  
  message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": REVIEW}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Готово` ✅\n> * Ждите написания отзыва, после завершите заказ с помощью кнопки `Завершить`"}]}]}}
  await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)
  clear_old_cache()

@bot.tree.command(name="оплата_payment", description="показать окно оплаты", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(amount="сумма")
async def payment(interaction: discord.Interaction, amount: int):
  if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
  if not interaction.channel.category or interaction.channel.category.id != TICKET_CREATE_CATEGORY: return await interaction.response.send_message("Вы не можете показывать оплату вне тикетов", ephemeral=True)
   
  message_data = {"flags": 36864, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"# <:866599434375528488:1508904126082187576> Оплата заказа\n### > Карта:\n{CARD}\n\n### > Сумма к оплате:\n{amount}₽\n\n### > Инструкция по оплате:\n1. Отправьте сумму на карту, указанную выше с комментарием «`Оплата заказа: {interaction.channel.name}`».\n2. После отправки средств нажмите на кнопку «Подтвердить оплату» и прикрепите скриншот с переводом в открывшемся окне."}]}]}
  
  msg = await bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=interaction.channel.id), json=message_data)
  new_view = discord.ui.View()
  new_view.add_item(PayOrder())
  new_view.add_item(UsePromo(bot))
  await interaction.channel.send(view=new_view)
  payment_cache[interaction.channel.id] = {"data": amount, "message_id": msg["id"], "manager": interaction.user.id}
  
  message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PAYMENT}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Готово` ✅\n> * Ждите оплаты заказа, вас пинганёт"}]}]}}
  await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)

@bot.tree.command(name="add", description="добавить пользователя в тикет", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="кого добавить")
async def add(interaction: discord.Interaction, user: discord.Member):
  if not any(role.id in STAFF or WORKERS for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете добавлять пользователей", ephemeral=True)
  if not interaction.channel.category or interaction.channel.category.id != TICKET_CREATE_CATEGORY and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете добавлять пользователей вне тикетов", ephemeral=True)
  await interaction.channel.set_permissions(user, view_channel=True, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
  message_data = {"type": 4, "data": {"flags": 36864, "components": [{"type": 17, "accent_color": 0x1ec45b, "components": [{"type": 12, "items": [{"media": {"url": user.display_avatar.url}}, {"media": {"url": interaction.user.display_avatar.url}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### {user.mention} добавлен в тикет ➕\n> * Удалить можно с помощью команды `/remove user:@{user.name}`"}]}]}}
  await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data)

@bot.tree.command(name="remove", description="убрать пользователя из тикета", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="кого убрать")
async def remove(interaction: discord.Interaction, user: discord.Member):
  if not any(role.id in STAFF or WORKERS for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете убирать пользователей", ephemeral=True)
  if not interaction.channel.category or interaction.channel.category.id != TICKET_CREATE_CATEGORY and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете убирать пользователей вне тикетов", ephemeral=True)
  await interaction.channel.set_permissions(user, overwrite=None, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
  message_data = {"type": 4, "data": {"flags": 36864, "components": [{"type": 17, "accent_color": 0xef5250, "components": [{"type": 12, "items": [{"media": {"url": user.display_avatar.url}}, {"media": {"url": interaction.user.display_avatar.url}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### {user.mention} удалён из тикета 🗑️\n> * Добавить можно с помощью команды `/add user:@{user.name}`"}]}]}}
  await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data)


class ConfigCommands(app_commands.Group):
  def __init__(self): super().__init__(name="panel", description="команды для работы с информационными сообщениями")

  @app_commands.command(name="info", description="обновить сообщение в 🔎・информация")
  async def info_panel(self, interaction: discord.Interaction):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)

    message_data = {"flags": 36864, "components": [
      {"type": 10, "content": "*—Че ваще за студия* `🔊🔎📂`"},
      {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": INFO_PANEL}}]},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Cutlass_Year:1488503994241519757> Информация"},
        {"type": 10, "content": f"*—Че ваще за **[MANERA]({INVITE})?***\n\n <:Exploding:1488501885374824448> **MANERA** — Стартап-студия по созданию рендеров / анимаций / тайтлов для людей которым нужны наши услуги или для **Minecraft** проектов, которым нужно **сотрудничество** с студией по созданию красивых визуалов для игры. У нас работают одни из лучших работников в Blender'е с **СНГ**!\n**Основанная** <@{ID_GUILD_OWNER}>  <t:1780765200>\n\n<:Thrive_Under_Pressure:1488501162544992416> Например Санёк хочёт заказать себе любой наш товар для своих нужд: аватарка для своего канала/превью/профиля/поста/в виде красивых обоев на устройство и тд.\n\n<:Food_Reserves:1488506081880576142> Здесь вы можете заказать работу по вашей задумке, лучшему качеству и 100%-ой реализацией выполнения.\n\n<:Critical_Hit:1488501686233469009> В **MANER'е** вы платите за скорость выполнения и качество. Если вам не понравилось качество выполнения или сроки ожидания, то сразу же сообщите это в тикете. Мы **быстро** разберёмся и **исправим** проблему."}
      ]},
      {"type": 17, "components": [
        {"type": 10, "content": "# <:Glowing:1488555982207320205> Как проходит заказ"},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "<:Death_Barter:1488505304529371177> Здесь, оформление и завершение твоего заказа проходит в несколько этапов: <:Arrow_Down_Highlighted:1488578347716972865> \n\n— `1.`  Выбираете товар в нашем боте и открываете тикет.\n\n— `2.` Расписываете своё тех-задание и загружаете исходники *(если имеются)*, по желанию можете выбрать с кем хотите работать из наших сотрудников *(если что, мы поможем с выбором работника для вашей идеи)*.\n\n— `3.` Обговариваете с нами мелкие детали заказа.\n\n— `4.` Мы отправляем вам номер карты на которую вы скидываете предоплату в размере **100%**.\n\n— `5.` После того как мы подтвердим что вы скинули денежную предоплату, мы **уведомим вас** и **начнём выполнение заказа**.\n\n— `6.` Мы отправляем вам заказ по этапам: *(добавляем **локацию**/**фон** → **персонажей**/**модели** → **свет** → **эффекты** → **анимируем**)*. В это время вы можете вносить правки, на этапе готового продукта правки не вносятся, только если сотрудник согласится снова зарендерить результат.\n\n— `7.` **Заказ завершён**! Вы получаете готовый продукт и можете оставить отзыв о нашей работе."},
        {"type": 14, "spacing": 1, "divider": True},
        
        {"type": 10, "content": "-# НИКОГДА НЕ СОМНЕВАЙСЯ В MANER`E!"}
      ]}
    ]}

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=INFO_CHANNEL_ID, message_id=INFO_MESSAGE_ID), json=message_data)
    
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": INFO_PANEL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Готово` ✅\n> * [перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{INFO_CHANNEL_ID}/{INFO_MESSAGE_ID}>)"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)
  
  @app_commands.command(name="catalog", description="обновить сообщение в 📜・каталог")
  async def catalog(self, interaction: discord.Interaction):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    
    message_data = {"flags": 36864, "components": [
      {"type": 10, "content": "*—Поясню за всё* `☠️🤙💀`"},
      {"type": 17, "components": [{"type": 12, "items": [{"media": {"url": CATALOG_PANEL}}]}]},
      
      {"type": 17, "components": [
        {"type": 10, "content": "# 🛒 Товар: FULL RENDER"},
        {"type": 12, "items": [{"media": {"url": FULL_RENDER}}]},
        {"type": 14, "spacing": 1, "divider": True},
        {"type": 10, "content": "### <:Netherite_Upgrade_Smithing_Templ:1495122438797660243> FULL RENDER\n* <:Brush:1503343652187930675> Рендер на локации/фоне c персонажами и моделями *(если они есть)*.\n\n◻ Все детали услуги обговариваются с рендермейкерами и администрацией в тикете вашего заказа."},
        {"type": 14, "spacing": 2, "divider": True},
        {"type": 10, "content": "## <:Arrow_Up_Highlighted:1503342014803087430>  Прайс: смотри в <#1428645265971351643> рендермейкеров<:Emerald:1503337138635149342>"}
      ]},
        
      {"type": 17, "components": [
        {"type": 10, "content": "# 🛒 Товар: CUSTOM ANIMATION"},
        {"type": 12, "items": [{"media": {"url": CUSTOM_ANIMATION}}]},
        {"type": 14, "spacing": 1, "divider": True},
        {"type": 10, "content": "### <:Axolotl:1503669257286717440> CUSTOM ANIMATION\n* <:Brush:1503343652187930675> Качественная анимация как в трейлерах.\n\n◻ Все детали услуги обговариваются с аниматорами и администрацией в тикете вашего заказа."},
        {"type": 14, "spacing": 2, "divider": True},
        {"type": 10, "content": "## <:Arrow_Up_Highlighted:1503342014803087430>  Прайс: в среднем изначальный рендер 899₽, затем по 249₽ за 1 секунду анимации<:Emerald:1503337138635149342>"}
      ]},
      
      {"type": 17, "components": [
        {"type": 10, "content": "# 🛒 Товар: MINECRAFT TITLE ANIMATION"},
        {"type": 12, "items": [{"media": {"url": MINECRAFT_TITLE_ANIMATION}}]},
        {"type": 14, "spacing": 1, "divider": True},
        {"type": 10, "content": "### <:Cherry_Hanging_Sign:1506355717303701587> MINECRAFT TITLE ANIMATION\n* <:Brush:1503343652187930675> Анимация кастомного майнкрафт заглавия.\n\n◻ Все детали услуги обговариваются с мультипликаторами и администрацией в тикете вашего заказа."},
        {"type": 14, "spacing": 2, "divider": True},
        {"type": 10, "content": "## <:Arrow_Up_Highlighted:1503342014803087430>  Прайс: в среднем 699₽<:Emerald:1503337138635149342>"},
        
        {"type": 14, "spacing": 1, "divider": True},
        {"type": 10, "content": F"-# По всем вопросам обращаться к <@{ID_GUILD_OWNER}> или [клик](<https://discord.com/users/{ID_GUILD_OWNER}>)"}
      ]}
    ]}

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=CATALOG_CHANNEL_ID, message_id=CATALOG_MESSAGE_ID), json=message_data)
    
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": CATALOG_PANEL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Готово` ✅\n> * [перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{CATALOG_CHANNEL_ID}/{CATALOG_MESSAGE_ID}>)"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)
   
  @app_commands.command(name="conditions", description="обновить сообщение в 🧷・условия-заказа")
  async def conditions_panel(self, interaction: discord.Interaction):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    
    message_data = {"flags": 36864, "components": [
      {"type": 10, "content": "*—Привет, прочти это* `📋🖍️📜`"},
      {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": CONDITIONS_PANEL}}]},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Icon_Search:1488796782178734100> Условия заказа"},
        {"type": 10, "content": "При оформлении заказа или сотрудничестве вы автоматически принимаете **все** ниже перечисленные **[условия](https://discord.com/channels/1428642884654993479/1428645046923563079/1494829581667143803)** 🔻"},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Hero_Of_The_Village:1488611638004154668> Оплата"},
        {"type": 10, "content": "— `1.` Вы платите 100% до получения заказа.\n\n— `2.` После отправки средств за заказ, средства не подлежат возврату.\n\n— `3.` Сейчас студия поддерживает оплату только в виде **рублей** *(в будущем будут добавлены другие способы оплаты)*.\n\n— `4.` В случаи отказа от вас скидывать 100%-ую предоплату ваш заказ будет удалён."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Iron_Pickaxe1:1488613802995093716> Работа над заказом"},
        {"type": 10, "content": "— `5.` Вы можете указать в бланке заполнения заказа с каким из всех наших сотрудников желаете работать.\n\n— `6.` Любой работник из студии может не принять ваш заказ в зависимости от его загруженности и его личных дел."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Clock_06:1488615381986840767> Время выполнения"},
        {"type": 10, "content": "— `7.` Ваш заказ может выполняться минимально от 2 полных дней *(в зависимости от тех-задания и занятости сотрудника)*.\n\n— `8.` Дедлайн создания вашего рендера может быт сдвинут на неопределенный срок из-за форс мажора *(вы будете проинформированы в этом случаи прямо в вашем тикете заказа и получите скидку)*."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Writable_Book1:1488616174206980096> Правки"},
        {"type": 10, "content": "— `9.` Наш сотрудник **имеет** право взять с вас доплату, в связи с многими правками *(будет обговорено с администрацией в тикете заказа)*.\n\n— `10.` Если вы вносите слишком много правок, администрация согласует их и может отказать дальнейшие правки *(работа над заказом продолжится дальше)*.\n\n— `11.` На финальном этапе заказа *(готовый продукт)*, правки не осуществляются **или** выполняются только по согласию с сотрудником."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Icon_Accessibility:1488795619542958120> Со стороны заказчиков"},
        {"type": 10, "content": "— `12.` Если вы сами отправили средства не на указанный счёт студии, заказ выполняться не будет.\n\n— `13.` В случае игнора с вашей стороны в течении 7 дней заказ будет заморожен, он будет добавлен в архив, когда вы вернётесь мы его разморозим."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Confirm:1488795080721694782> Отзывы"},
        {"type": 10, "content": "— `14.` После завершения заказа, вы можете написать отзыв и поставить колличество звезд."}
      ]}
    ]}

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=CONDITIONS_CHANNEL_ID, message_id=CONDITIONS_MESSAGE_ID), json=message_data)
    
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": CONDITIONS_PANEL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Готово` ✅\n> * [перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{CONDITIONS_CHANNEL_ID}/{CONDITIONS_MESSAGE_ID}>)"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)
  
  @app_commands.command(name="placing_an_order", description="обновить сообщение в ✍・заказать")
  async def placing_an_order_panel(self, interaction: discord.Interaction):
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.response.send_message("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    
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

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=PLACING_AN_ORDER_CHANNEL_ID, message_id=PLACING_AN_ORDER_MESSAGE_ID), json=message_data)
    
    message_data1 = {"type": 4, "data": {"flags": 36928, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": PLACING_AN_ORDER_PANEL}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"### `Готово` ✅\n> * [перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{PLACING_AN_ORDER_CHANNEL_ID}/{PLACING_AN_ORDER_MESSAGE_ID}>)"}]}]}}
    await bot.http.request(discord.http.Route("POST", "/interactions/{interaction_id}/{interaction_token}/callback", interaction_id=interaction.id, interaction_token=interaction.token), json=message_data1)


bot.tree.add_command(WorkersCommands(), guild=discord.Object(id=GUILD_ID))
bot.tree.add_command(PromoCommands(), guild=discord.Object(id=GUILD_ID))
#bot.tree.add_command(ConfigCommands(), guild=discord.Object(id=GUILD_ID))
