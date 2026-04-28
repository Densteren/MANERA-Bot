import discord
from discord.ext import commands
from discord import app_commands
from views.close_ticket import CloseView
from views.select_ticket_type import TicketTypeSelect
from views.appoint_ticket import RenderView
from config import GUILD_ID, MEMBER_ROLE, STAFF, ID_GUILD_OWNER, RENDERMAKER_FORUM_ID, TICKET_CREATE_CATEGORY, CARD, INVITE, INFO_CHANNEL_ID, INFO_MESSAGE_ID, CONDITIONS_CHANNEL_ID, CONDITIONS_MESSAGE_ID, PLACING_AN_ORDER_CHANNEL_ID, PLACING_AN_ORDER_MESSAGE_ID
from images.images_url import PAYMENT, INFO_PANEL, CONDITIONS_PANEL, PLACING_AN_ORDER_PANEL
from fs import CloseDMView
bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

@bot.event
async def on_ready():
  print(f"[DEBUG] {bot.user} готов!")
    
  bot.add_view(TicketTypeSelect(bot))
  bot.add_view(CloseView())
  bot.add_view(RenderView())
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
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound): return


class RendermakerCommands(app_commands.Group):
  def __init__(self): super().__init__(name="rendermaker", description="команды для работы с портфолио рендермейкеров")
  
  @app_commands.command(name="add", description="добавить портфолио для рендермейкера")
  @app_commands.describe(user="рендермейкер", rendermaker="Никнейм (название публикации)", bio="Описание / биография", url="Ссылка на изображение (1 главное изображение)", price="Цена (в среднем в ₽)")
  async def rendermaker_add(self, interaction: discord.Interaction, user: discord.Member, rendermaker: str, bio: str, url: str, price: int):
    await interaction.response.defer(ephemeral=True)
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете воспользоваться этой коммандой", ephemeral=True)
  
    message_data = {"name": f"{rendermaker}", "message": {"flags": 36864, "components": [{"type": 17, "components": [{"type": 12, "items": [{"media": {"url": f"{url}"}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"# {rendermaker}\n### > Bio:\n{bio.replace('\\n', '\n')}\n\n## > Price: в среднем {price}₽"}]}]}}
    
    msg = await bot.http.request(discord.http.Route("POST", "/channels/{forum_id}/threads", forum_id=RENDERMAKER_FORUM_ID), json=message_data, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
    thread_id = msg["id"]
    thread = interaction.guild.get_channel(thread_id)
    if thread is None:
      try: thread = await interaction.guild.fetch_channel(thread_id)
      except Exception: return await interaction.followup.send("Ошибка: ветка не найдена или ID неверный", ephemeral=True)
    msg_td = await thread.send(f"{user.mention}")
    await msg_td.delete()
    await interaction.followup.send(f"[перейти к сообщению](<https://discord.com/channels/{GUILD_ID}/{thread_id}/{thread_id}>)", ephemeral=True)

  @app_commands.command(name="edit", description="редактировать портфолио для рендермейкера")
  @app_commands.describe(id="ID сообщения / ветки в 📍・портфолио", rendermaker="Никнейм (название публикации)", bio="Описание / биография", url="Ссылка на изображение (1 главное изображение)", price="Цена (в среднем в ₽)")
  async def rendermaker_edit(self, interaction: discord.Interaction, id: str, rendermaker: str, bio: str, url: str, price: int):
    await interaction.response.defer(ephemeral=True)
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете воспользоваться этой коммандой", ephemeral=True)
  
    message_data = {"flags": 36864,"components": [{"type": 17,"components": [{"type": 12, "items": [{"media": {"url": f"{url}"}}]}, {"type": 14, "spacing": 2, "divider": True}, {"type": 10, "content": f"# {rendermaker}\n### > Bio:\n{bio.replace('\\n', '\n')}\n\n## > Price: в среднем {price}₽"}]}]}
  
    thread = interaction.guild.get_channel(id)
    if thread is None:
      try: thread = await interaction.guild.fetch_channel(id)
      except Exception: return await interaction.followup.send("Ошибка: ветка не найдена или ID неверный", ephemeral=True)
    if thread.name != rendermaker: await thread.edit(name=rendermaker, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
    await bot.http.request(discord.http.Route("PATCH", "/channels/{message_id}/messages/{message_id}", message_id=int(id)), json=message_data)
    await interaction.followup.send(f"[перейти к сообщению](<https://discord.com/channels/{interaction.guild.id}/{int(id)}/{int(id)}>)", ephemeral=True)

  @app_commands.command(name="delete", description="удалить портфолио для рендермейкера")
  @app_commands.describe(id="ID сообщения / ветки в 📍・портфолио")
  async def rendermaker_delete(self, interaction: discord.Interaction, id: str):
    await interaction.response.defer(ephemeral=True)
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете воспользоваться этой коммандой", ephemeral=True)
  
    thread = interaction.guild.get_channel(id)
    if thread is None:
      try: thread = await interaction.guild.fetch_channel(id)
      except Exception: return await interaction.followup.send("Ошибка: ветка не найдена или ID неверный", ephemeral=True)
    await thread.delete(reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
    await interaction.followup.send(f"удалено", ephemeral=True)


@bot.command(name="оплата")
async def payment(ctx):
  if not any(role.id in STAFF for role in ctx.author.roles): return
  if ctx.channel.category_id != TICKET_CREATE_CATEGORY: return
  if ctx.message.content.strip() != "оплата": return
    
  message_data = {"flags": 36864, "components": [
    {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": {PAYMENT}}}]},
        {"type": 14, "spacing": 2, "divider": True},
        {"type": 10, "content": f"# Оплата\n### > Карта:\n{CARD}"}
    ]}
  ]}
  
  await bot.http.request(discord.http.Route("POST", "/channels/{channel_id}/messages", channel_id=ctx.channel.id), json=message_data)

@bot.tree.command(name="add", description="добавить пользователя в тикет", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="кого добавить")
async def add(interaction: discord.Interaction, user: discord.Member):
  await interaction.response.defer()
  if not any(role.id in STAFF or role.id == 1437131949264080937 for role in interaction.user.roles): return await interaction.followup.send("Вы не можете добавлять пользователей", ephemeral=True)
  if interaction.channel.category.id != TICKET_CREATE_CATEGORY and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете добавлять пользователей вне тикетов", ephemeral=True)
  #await interaction.response.defer()
  await interaction.channel.set_permissions(user, view_channel=True, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
  embed = discord.Embed(description=f"{user.mention} добавлен в тикет {interaction.channel.mention}", color=0x1ec45b)
  await interaction.followup.send(embed=embed, silent=True)

@bot.tree.command(name="remove", description="убрать пользователя из тикета", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="кого убрать")
async def remove(interaction: discord.Interaction, user: discord.Member):
  await interaction.response.defer()
  if not any(role.id in STAFF or role.id == 1437131949264080937 for role in interaction.user.roles): return await interaction.followup.send("Вы не можете убирать пользователей", ephemeral=True)
  if interaction.channel.category.id != TICKET_CREATE_CATEGORY and not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете убирать пользователей вне тикетов", ephemeral=True)
  await interaction.channel.set_permissions(user, overwrite=None, reason=f"ЗАПРОС КОММАНДОЙ ОТ {interaction.user.name}")
  embed = discord.Embed(description=f"{user.mention} удалён из тикета {interaction.channel.mention}", color=0xef5250)
  await interaction.followup.send(embed=embed, silent=True)


class ConfigCommands(app_commands.Group):
  def __init__(self): super().__init__(name="panel", description="команды для работы с информационными сообщениями")

  @app_commands.command(name="info", description="обновить сообщение в 🔎・информация")
  async def info_panel(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    
    message_data = {"flags": 36864, "components": [
      {"type": 10, "content": "*—Че ваще за студия* `🔊🔎📂`"},
      {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": {INFO_PANEL}}}]},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Cutlass_Year:1488503994241519757> Информация"},
        {"type": 10, "content": f"*—Че ваще за **[MANERA]({INVITE})?***\n\n <:Exploding:1488501885374824448> **MANERA** —  Стартап-студия по созданию рендеров для людей которым нужны наши услуги или для **Minecraft** проектов, которым нужно **сотрудничество** с студией по созданию красивых визуалов для игры. У нас работают одни из лучших рендерМейкеров с **СНГ**!\n**Основанная** <@{ID_GUILD_OWNER}>  <t:1774170060:D>\n\n<:Thrive_Under_Pressure:1488501162544992416> Например Санёк хочёт заказать себе любой наш товар для своих нужд: аватарка для своего канала/превью/профиля/поста/в виде красивых обоев на устройство и тд.\n\n<:Food_Reserves:1488506081880576142> Здесь вы можете заказать рендер по вашей задумке, лучшему качеству и 100% реализацией выполнения.\n\n<:Critical_Hit:1488501686233469009> В **MANER`е** вы платите за скорость выполнения и качество. Если вам не понравилось качество выполнения или сроки ожидания, то сразу же сообщите это в тикете. Мы **быстро** разберёмся и **исправим** проблему."}
      ]},
      {"type": 17, "components": [
        {"type": 10, "content": "# <:Glowing:1488555982207320205> Как проходит заказ"},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "<:Death_Barter:1488505304529371177> Здесь, оформление и завершение твоего заказа проходит в несколько этапов: <:Arrow_Down_Highlighted:1488578347716972865> \n\n— `1.`  Выбираете товар в нашем боте и открываете тикет.\n\n— `2.` Расписываете своё тех-задание, по желанию можете выбрать с кем хотите работать из наших сотрудников *(если что, мы поможем с выбором работника для вашей идеи)*.\n\n— `3.` Обговариваете с нами мелкие детали заказа.\n\n— `4.` Мы отправляем вам номер карты на которую вы скидываете предоплату в размере **100%**.\n\n— `5.` После того как мы подтвердим что вы скинули денежную предоплату, мы **уведомим вас** и **начнём выполнение заказа**.\n\n— `6.` Мы отправляем вам рендер по этапам *(добавляем **локацию** → **персонажей**/**модели** → **свет** → **эффекты**)*. В это время вы можете вносить правки, на этапе финального рендера правки не вносятся, только если сотрудник согласится внести правку на этом этапе и снова зарендерить финальный результат."},
        {"type": 14, "spacing": 1, "divider": True},
        
        {"type": 10, "content": "-# НИКОГДА НЕ СОМНЕВАЙСЯ В MANER`E!"}
      ]}
    ]}

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=INFO_CHANNEL_ID, message_id=INFO_MESSAGE_ID), json=message_data)
    await interaction.followup.send("готово", ephemeral=True)
    
  @app_commands.command(name="conditions", description="обновить сообщение в 🧷・условия-заказа")
  async def conditions_panel(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    
    message_data = {"flags": 36864, "components": [
      {"type": 10, "content": "*—Привет, прочти это* `📋🖍️📜`"},
      {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": CONDITIONS_PANEL}}]},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Icon_Search:1488796782178734100> Условия заказа"},
        {"type": 10, "content": "При оформлении заказа или сотрудничестве вы автоматически принимаете **все** ниже перечисленные **[условия](https://discord.com/channels/1428642884654993479/1428645046923563079/1494829581667143803)** 🔻"},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Hero_Of_The_Village:1488611638004154668> Оплата"},
        {"type": 10, "content": "— `1.` Вы платите 100% до получения заказа.\n\n— `2.` После отправки средств за заказ, средства не подлежат возврату.\n\n— `3.` В течении времени пока заказ ещё не начал выполняться, есть возможность вернуть **90%** средств если вы передумали заказывать услугу.\n\n— `4.` В случаи отказа от вас скидывать 100%-ую предоплату ваш заказ будет удалён."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Iron_Pickaxe1:1488613802995093716> Работа над заказом"},
        {"type": 10, "content": "— `5.` Вы можете указать в бланке заполнения заказа с каким из всех наших сотрудников желаете работать.\n\n— `6.` Любой работник из студии может не принять ваш заказ в зависимости от его загруженности и его личных дел."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Clock_06:1488615381986840767> Время выполнения"},
        {"type": 10, "content": "— `7.` Ваш заказ может выполняться минимально от 2 полных дней *(в зависимости от тз и личной жизни сотрудника)*.\n\n— `8.` Дедлайн создания вашего рендера может быт сдвинут на неопределенный срок из-за форс мажора *(вы будете проинформированы в этом случаи прямо в вашем тикете заказа и получите скидку)*."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Writable_Book1:1488616174206980096> Правки"},
        {"type": 10, "content": "— `9.` Наш сотрудник **имеет** право взять с вас доплату, в связи с многими правками *(будет обговорено с администрацией)*.\n\n— `10.` Если вы вносите слишком много правок, администрация согласует их и может дать решение на отказ от такого множества правок *(работа над рендером продолжится дальше)*.\n\n— `11.` На финальном этапе заказа *(финальный рендер изображения)*, правки не осуществляются **или** осуществляются и выполняются только по согласованию с сотрудником."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Icon_Accessibility:1488795619542958120> Со стороны заказчиков"},
        {"type": 10, "content": "— `12.` Если вы сами неправильно отправили средства не на указанный счёт студии, заказ выполняться не будет.\n\n— `13.` В случае игнора с вашей стороны в течении 14 дней заказ будет заморожен, он будет добавлен в архив, когда вы вернётесь мы его разморозим."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# <:Confirm:1488795080721694782> Отзывы"},
        {"type": 10, "content": "— `14.` После завершения заказа, вы можете написать текст для вашего отзыва, в случаи отказа от написании отзыва, отзыв будет отправлен без вашего комментария *(только результат заказа)*."}
      ]}
    ]}

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=CONDITIONS_CHANNEL_ID, message_id=CONDITIONS_MESSAGE_ID), json=message_data)
    await interaction.followup.send("готово", ephemeral=True)
  
  @app_commands.command(name="placing_an_order", description="обновить сообщение в ✍・заказать")
  async def placing_an_order_panel(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not any(role.id in STAFF for role in interaction.user.roles): return await interaction.followup.send("Вы не можете воспользоваться этой коммандой", ephemeral=True)
    
    message_data = {"flags": 36864, "components": [
      {"type": 17, "components": [
        {"type": 12, "items": [{"media": {"url": PLACING_AN_ORDER_PANEL}}]},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 10, "content": "# Оформление заказа"},
        {"type": 10, "content": "Заказывай в MANER`E\nМы создадим рендер по твоему тех-заданию в наилучшем виде и реализации."},
        {"type": 14, "spacing": 2, "divider": True},
        
        {"type": 1, "components": [{"type": 3, "custom_id": "ticket:placing_an_order", "placeholder": "Выберите нужное", "max_values": 1, "options": [{"label": "Рендер", "value": "render", "emoji": {"name": "Netherite_Upgrade_Smithing_Templ", "id": 1495122438797660243}, "default": False}]}]},
        #{"type": 1, "components": [{"type": 2, "style": 2, "label": "Рендер", "emoji": {"name": "Netherite_Upgrade_Smithing_Templ", "id": 1495122438797660243}, "custom_id": "ticket_button:placing_an_order"}]},
        {"type": 1, "components": [{"type": 2, "style": 2, "label": "Очистить выбор", "emoji": {"name": "Wind_Charged", "id": 1488847018930737262},"custom_id": "ticket:clear"}]},
        {"type": 14, "spacing": 1, "divider": True},
        
        {"type": 10, "content": F"-# По всем вопросам обращаться к <@{ID_GUILD_OWNER}> или [клик](<https://discord.com/users/{ID_GUILD_OWNER}>)"}
      ]}
    ]}

    await bot.http.request(discord.http.Route("PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=PLACING_AN_ORDER_CHANNEL_ID, message_id=PLACING_AN_ORDER_MESSAGE_ID), json=message_data)
    await interaction.followup.send("готово", ephemeral=True)


bot.tree.add_command(RendermakerCommands(), guild=discord.Object(id=GUILD_ID))