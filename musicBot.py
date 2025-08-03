import logger
import discord
from discord.ext import commands
import asyncio
import api.bilibiliApi as bApi
import json

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player = None

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hello Dicord Bot!')

    @commands.command(name="你好")
    async def chinese(self, ctx):
        await ctx.send("I don't speak chinese.")

    @commands.command()
    async def github(self, ctx):
        """ Reply the github repository of this bot """
        await ctx.send("See: https://github.com/whitefood0201/bilibili-discord-music-bot")

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
    async def stop(self, ctx: commands.context.Context):
        """Stops and disconnects the bot from voice"""

        # clear the last audio data, if it exists
        if self.player:
            self.player.cleanup()
        
        await ctx.send("Bye~")
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx: commands.context.Context, bvid):
        if bvid == None:
            return await ctx.send('You have to pass a bvid!')

        if ctx.voice_client == None:
            await self.join(ctx)
        
        try:
            url = bApi.getAudio(bvid)
            if url == "":
                return await ctx.send('Video not found, please check the bvid!')
            
            self.player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
            
            await ctx.send("playing {bvid}")
            return ctx.voice_client.play(self.player)
        except Exception as e:
            print(e)
        
        return await ctx.send('Error Ocurred, please try again. \nIf this happed many time, try contact with the Administrator!')


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
        await bot.add_cog(Music(bot))
        await bot.start(config["token"])

CONFIG = {}
with open("./config.json") as f:
    CONFIG = json.load(f)
asyncio.run(main(CONFIG))