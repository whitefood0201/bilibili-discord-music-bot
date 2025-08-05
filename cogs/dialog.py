from discord.ext import commands

class Dialog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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