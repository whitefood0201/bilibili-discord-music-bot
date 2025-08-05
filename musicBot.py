import logger
import discord
from discord.ext import commands
import asyncio
import json
from cogs.musicCog import MusicManager
from cogs.dialog import Dialog

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='Q', intents=intents)
    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')

async def main(config):
    logger.setupLogger('discord')
    async with bot:
        await bot.add_cog(MusicManager(bot))
        await bot.add_cog(Dialog(bot))
        await bot.start(config["token"])

CONFIG = {}
with open("./config.json") as f:
    CONFIG = json.load(f)
asyncio.run(main(CONFIG))