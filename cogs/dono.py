import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Dono(commands.Cog, name="Dono"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
        name="sy",
        description="Sincroniza os comandos de barra.",
    )
    @app_commands.describe(scope="O escopo da sincronização. Pode ser `glo` ou `gui`")
    @commands.is_owner()
    async def sync(self, context: Context, scope: str) -> None:

        if scope == "glo":
            await context.bot.tree.sync()
            embed = discord.Embed(
                description="Os comandos de barra foram sincronizados globalmente.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        elif scope == "gui":
            context.bot.tree.copy_global_to(guild=context.guild)
            await context.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description="Os comandos de barra foram sincronizados neste servidor.",
                color=0xBEBEFE,
            )
            await context.send(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            description="O escopo deve ser `glo` ou `gui`.", color=0xE02B2B
        )
        await context.send(embed=embed, ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(Dono(bot))