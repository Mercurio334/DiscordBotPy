from discord.ext import commands
import discord
import yt_dlp as youtube_dl
import asyncio
import time

# Configurações do yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'preferredquality': '192',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'geo_bypass': True
}

class Musica(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.is_playing = False
        self.loop = False
        self.voice_client = None
        self.disconnect_timer = None
        self.current_song = None

    async def disconnect_if_empty(self):
        while self.voice_client:
            await asyncio.sleep(20)
            if not self.voice_client.is_playing() and not [member for member in self.voice_client.channel.members if not member.bot]:
                await self.voice_client.disconnect()
                self.voice_client = None
                self.is_playing = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id and before.channel is not None and after.channel is None:
            self.is_playing = False
            self.voice_client = None

    @commands.hybrid_command(name="play", description="Link / Nome")
    async def play(self, ctx, *, musica: str):
        if not ctx.author.voice:
            return await ctx.send("Você precisa estar em um canal de voz para usar este comando.")

        if not self.voice_client or not self.voice_client.is_connected():
            self.voice_client = await ctx.author.voice.channel.connect()
        
        custom_emoji = '<a:car_45:1272318895977660457>'
        embed_loading = discord.Embed(description=f"{custom_emoji} **Procurando a música...**", color=0x414045)
        loading_message = await ctx.send(embed=embed_loading)

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.cache.remove()
                info = ydl.extract_info(f"ytsearch1:{musica}", download=False)
                if not info or 'entries' not in info or len(info['entries']) == 0:
                    await loading_message.delete()
                    return await ctx.send("❌ Nenhum resultado encontrado para sua busca.", ephemeral=True)
                video_info = info['entries'][0]
                url = video_info['url']
                title = video_info['title']
                contador = video_info['duration']
                thumbnail = video_info['thumbnail']

            self.current_song = {'url': url, 'title': title, 'thumbnail': thumbnail}
            ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
            self.voice_client.stop()
            self.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: self.check_loop())

            minutes, seconds = divmod(contador, 60)
            embed_playing = discord.Embed(description=f"▶ **Tocando:** {title}\n⏱ Duração: " "{:02d}:{:02d}".format(minutes, seconds), color=0x414045)
            embed_playing.set_thumbnail(url=thumbnail)
            await loading_message.edit(embed=embed_playing)
        except Exception as e:
            await loading_message.delete()
            await ctx.send(f"❌ Um erro inesperado aconteceu. {e}", ephemeral=True)
            print(f" UM ERRO ENCONTRADO. {e}")

        if not self.disconnect_timer:
            self.disconnect_timer = self.bot.loop.create_task(self.disconnect_if_empty())

        start_time = time.time()

        while self.voice_client and self.voice_client.is_playing():
            current_time = time.time()
            elapsed_time = current_time - start_time
            contador2 = int(elapsed_time)
            minutes, seconds = divmod(contador2, 60)
            embed_playing = discord.Embed(description=f"▶ **Tocando:** {title}\n⏱ Duração: " "{:02d}:{:02d}".format(minutes, seconds), color=0x414045)
            embed_playing.set_thumbnail(url=thumbnail)
            await loading_message.edit(embed=embed_playing)
            await asyncio.sleep(0.1)
            
            
    def check_loop(self):
        if self.loop and self.current_song:
            asyncio.run_coroutine_threadsafe(self.repeat_current_song(), self.bot.loop)
        else:
            self.is_playing = False

    async def repeat_current_song(self):
        if self.current_song:
            url = self.current_song['url']
            ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            self.voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options), after=lambda e: self.check_loop())

    @commands.hybrid_command(name="loop", description="Ativa/desativa o loop da música")
    async def loop(self, ctx):
        self.loop = not self.loop
        estado = "ativado" if self.loop else "desativado"
        embed = discord.Embed(description=f"🔄 **Loop {estado}.**", color=0x414045)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="stop", description="Para a música")
    async def stop(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            self.is_playing = False
            self.loop = False
            await self.voice_client.disconnect()
            self.voice_client = None

        embed = discord.Embed(description="⏹ **Música parada e bot desconectado.**", color=0x414045)
        await ctx.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Musica(bot))
