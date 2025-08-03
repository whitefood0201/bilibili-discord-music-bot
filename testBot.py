import logger
import discord
from discord.ext import commands
import asyncio
import discord.ext
import discord.ext.commands 
import api.bilibiliApi as bApi
import json

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello Dicord Bot!')

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.author.voice == None:
            return await ctx.send("You have to join a voice channel")
        
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, bvid):
        if bvid == None:
            return await ctx.send('You have to pass a bvid!')

        if ctx.voice_client == None:
            await self.join(ctx)
        
        try:
            url = bApi.getAudio(bvid)
            if url == "":
                return await ctx.send('Video not found, please check the bvid!')
            
            player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
            return ctx.voice_client.play(player)
        except Exception as e:
            print(e)
        
        return await ctx.send('Error Ocurred, please try again. \nIf this happed many time, try contact with the Administrator!')


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)
    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')

async def main(config):
    logger.setupLogger('discord')
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(config["token"])

CONFIG = {}
with open("./config.json") as f:
    CONFIG = json.load(f)
asyncio.run(main(CONFIG))