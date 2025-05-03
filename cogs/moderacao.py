from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Moderacao(commands.Cog, name="Moderação"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="excluir",
        description="Exclua várias mensagens.",
    )
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @app_commands.describe(quant="A quantidade de mensagens que devem ser excluídas.")
    @commands.is_owner()
    async def purge(self, context: Context, quant: int) -> None:

        await context.send(
            "Excluindo mensagens..."
        )  
        purged_messages = await context.channel.purge(limit=quant + 1)
        embed = discord.Embed(
            description=f"**{context.author}** limpo **{len(purged_messages)-1}** mensagens!",
            color=0x414045,
        )
        await context.channel.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Moderacao(bot))
