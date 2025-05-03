import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import Activity, ActivityType, Streaming

class Geral(commands.Cog, name="Geral"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="botinfo",
        description="Obtenha informações sobre o bot.",
    )
    @commands.is_owner()
    async def botinfo(self, context: Context) -> None:

        embed = discord.Embed(
            color=0x414045,
        )
        embed.set_author(name="informações do Bot")
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands)",
            inline=False,
        )
        embed.set_footer(text=f"Requerido por {context.author}")
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(
        name="ping",
        description="Verifique o ping do bot .",
    )
    async def ping(self, context: Context) -> None:
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"A latência do bot é {round(self.bot.latency * 1000)}ms.",
            color=0x414045,
        )
        await context.send(embed=embed, ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(Geral(bot))
