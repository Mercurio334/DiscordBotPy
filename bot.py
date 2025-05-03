import json
import logging
import os
import platform
import random
import sys


import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv
import tracemalloc

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' não encontrado! Adicione-o e tente novamente.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.all()
intents.members = True

class LoggingFormatter(logging.Formatter):
    white = "\x1b[37m"
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.blue + self.bold)
        formatter = logging.Formatter(format, "[%Y-%m-%d %H:%M]", style="{")
        return formatter.format(record)

logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "[%Y-%m-%d %H:%M]", style="{"
)
file_handler.setFormatter(file_handler_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

class DiscordBot(commands.Bot):
    def __init__(self, **options) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
            **options
        )
        self.logger = logger
        self.config = config
        self.last_log_line = None
        self.tracemalloc = None

    # LOG POR CANAL     
    @tasks.loop(minutes=1.0)
    async def send_log_lines(self):
        channel_id = 123  # Substitua pelo ID do seu canal
        channel = self.get_channel(channel_id)
        if not channel:
            print(f"Canal com id {channel_id} não encontrado")
            return
        with open("discord.log", "r", encoding='utf-8') as file:
            lines = file.readlines()
        last_line = lines[-1]
        if last_line != self.last_log_line:
            embed = discord.Embed(
            description=f"```{last_line}```",
            color=0xff7700,
            )
            await channel.send(embed=embed)
            self.last_log_line = last_line

    async def on_ready(self):
        print('log por canal online')
        self.send_log_lines.start()

    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Extensão carregada '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Falha ao carregar a extensão {extension}\n{exception}"
                    )

    # STATUS CUSTOM
    @tasks.loop(seconds=5)
    async def status_task(self) -> None:
        try:
            status = ["Bot Test 1", "Bot Test 2"]
            if status:
                def obter_texto_status():
                    return random.choice(status)
                chosen_status = obter_texto_status()
                activity_name = chosen_status
                activity = discord.CustomActivity(name=activity_name)
                await self.change_presence(activity=activity)
            else:
                self.logger.warning("Nenhum status encontrado")
        except Exception as e:
            self.logger.error(f"Erro ao buscar status {e}")

    @status_task.before_loop
    async def before_status_task(self) -> None:
        self.logger.info("Esperando o bot estar pronto para iniciar a tarefa de status...")
        await self.wait_until_ready()
        self.logger.info("terefa de status ativa!!")
        tracemalloc.start()

    async def setup_hook(self) -> None:
        self.logger.info(f"logado como {self.user.name}")
        self.logger.info(f"discord.py API versão: {discord.__version__}")
        self.logger.info(f"Python versão: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("----------comandos---------")
        await self.load_cogs()
        self.status_task.start()
        

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executado {executed_command} comando em {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )

    async def on_command_error(self, context: Context, error) -> None:
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="Você não é o dono do bot!", color=0xE02B2B
            )
            await context.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="ERRO!",
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed, ephemeral=True)
        else:
            self.logger.error(f"Exceção não tratada em comando '{context.command}'.", exc_info=error)
            raise error

load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))
