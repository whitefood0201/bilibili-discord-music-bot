import discord
from discord.ext import commands
import api.bilibiliApi as bApi
import asyncio

def isEmpty(l: list):
    return len(l) == 0

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastVidoData = None
        self.player = None
        self.stoped = False
        self.queue = []
    
    def clear(self):
        # clear the music status
        self.queue = []
        self.player = None
        self.lastVidoData = None

    async def stop(self, ctx):
        self.stoped = True
        if ctx.voice_client != None:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        self.clear()
        await ctx.send("Bye~")

    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.author.voice == None:
            return await ctx.send("You have to join a voice channel!")
        
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)        
        try:
            await channel.connect()
        except discord.ClientException:
            await ctx.send("I'm can't connect to the channel, please give me the permissions.")
        
        # make sure
        t = 0
        while not ctx.voice_client.is_connected():
            if (t > 30):
                await ctx.send("I'm traveling on the Moon, can't the voice channel (Connnect Timeout).")
                return
            await asyncio.sleep(0.1)
            t+=1
        self.stoped = False
    
    async def play(self, ctx, bvid):
        """ Play a audio or add it to the end of playlist """
        if bvid == None:
            return await ctx.send('You have to pass a bvid!')

        data = bApi.getVideoData(bvid)
        if data == None:
            return await ctx.send('Video not found, please check the bvid!')
        
        try:
            if isEmpty(self.queue) and self.player == None: # playlist is empty and not playing
                await self.playAudio(ctx, data)
            else: # is playing => add to the queue
                await ctx.send(f'Added `{data["bvid"]}: {data["title"]}` to the playlist~')
            
            self.queue.append(data)
            return
        except Exception as e:
            e.with_traceback()
        
        return await ctx.send('Error Ocurred, please try again. \nIf this happed many time, try contact with the Administrator!')
    
    async def showQueue(self, ctx):
        """ Show the playlist """
        if isEmpty(self.queue):
            return await ctx.send('```Empty Playlist```')

        msg = f'```\nPlayList: size[{len(self.queue)}]: \n'
        for i, d in enumerate(self.queue):
            msg += f' {i+1}. {d["bvid"]}: {d["title"]} {" <-- Playing" if i==0 else ""}\n'
        msg += "```"
        await ctx.send(msg)
    
    async def skip(self, ctx):
        """ Skip the playing audio """
        await ctx.send("I'm skipping the playing video~")
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await self.next(ctx)
    
    async def next(self, ctx):
        if self.stoped:
            return
        if isEmpty(self.queue):
            return await ctx.send("Get to the end of Playlist~")
        data = self.queue[0]
        await self.playAudio(ctx, data)

    async def playLast(self, ctx):
        data = self.lastVidoData
        if data == None:
            await ctx.send("I don't remember the last video ＞︿＜")
        await self.playAudio(ctx, data)
    
    async def playAudio(self, ctx, data):
        """ play a audio """
        url = bApi.getAudioBaseUrl(data["bvid"], data["cid"])
        
        async def after(e):
            if e != None:
                await ctx.send(f'Error when playing `{data["bvid"]}: {data["title"]}`, skipped!')
            if ctx.voice_client != None:
                self.player = None
                self.queue.pop(0)
                await self.next(ctx)
        
        try:
            await ctx.send(f'playing `{data["bvid"]}: {data["title"]}`')
            self.player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
            ctx.voice_client.play(self.player, after= lambda e: self.bot.loop.create_task(after(e)))
            self.lastVidoData = data
        except Exception as e:
            e.with_traceback()
            await ctx.send(str(e))


class MusicManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guildMusicInstances = {}

    def getMusicInstance(self, guildId: int) -> Music:
        if guildId not in self.guildMusicInstances:
            self.guildMusicInstances[guildId] = Music(self.bot)
        return self.guildMusicInstances[guildId]
    
    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        music = self.getMusicInstance(ctx.guild.id)
        await music.join(ctx)

    @commands.command(name="bye")
    async def stop(self, ctx: commands.context.Context):
        """Stops and disconnects the bot from voice"""
        music = self.getMusicInstance(ctx.guild.id)
        await music.stop(ctx)

    @commands.command()
    async def play(self, ctx, bvid):
        """ Play a audio or add it to the end of playlist """
        music = self.getMusicInstance(ctx.guild.id)
        await music.play(ctx, bvid)
    
    @commands.command()
    async def queue(self, ctx):
        """ Show the playlist """
        music = self.getMusicInstance(ctx.guild.id)
        await music.showQueue(ctx)
    
    @commands.command()
    async def skip(self, ctx):
        """ Skip the playing audio """
        music = self.getMusicInstance(ctx.guild.id)
        await music.skip(ctx)
    
    @commands.command()
    async def again(self, ctx):
        """ play the last video """
        music = self.getMusicInstance(ctx.guild.id)
        await music.playLast(ctx)

    @play.before_invoke
    @again.before_invoke
    async def ensureConnected(self, ctx):
        if ctx.voice_client == None:
            music = self.getMusicInstance(ctx.guild.id)
            await music.join(ctx)
            # await ctx.send("I'm not connect to a voice~")
            # raise commands.CommandError("Not Connected")

    @skip.before_invoke
    async def ensurePlaying(self, ctx):
        music = self.getMusicInstance(ctx.guild.id)
        if music.queue == []:
            await ctx.send("I'm not playing any thing~")
            raise commands.CommandError("No audio playing!")
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user:
            if before.channel is not None and after.channel is None:
                guildId = before.channel.guild.id
                if guildId in self.guildMusicInstances:
                    self.guildMusicInstances[guildId].clear()
        