from dotenv import load_dotenv
from bot import bot
from os import getenv
load_dotenv()

if __name__ == "__main__":
    bot.run(getenv("BOT_TOKEN"))