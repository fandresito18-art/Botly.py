import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# 🔹 CARGAR VARIABLES DE ENTORNO
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

CANAL_PROHIBIDO_ID = 1494972441628508200

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

    canal = await bot.fetch_channel(CANAL_PROHIBIDO_ID)

    async for msg in canal.history(limit=10):
        if msg.author == bot.user:
            return

    embed = discord.Embed(
        title="Ilegal Target | Auto Mod",
        description="Este canal está monitoreado por el sistema de seguridad automatizado del servidor.",
        color=0x2b2d31
    )

    embed.add_field(
        name="Si escribes en este canal sin autorización:",
        value="• Serás baneado automáticamente.\n"
              "• Tu mensaje será eliminado.",
        inline=False
    )

    embed.add_field(
        name="⚠️ Aviso",
        value="Si puedes ver este canal por error, **no envíes ningún mensaje.**",
        inline=False
    )

    embed.set_footer(text="Ilegal Target Security System")

    await canal.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CANAL_PROHIBIDO_ID:
        try:
            await message.delete()
        except:
            pass

        try:
            await message.author.send(
                "🚫 Has sido baneado por escribir en un canal restringido en Ilegal Target."
            )
        except:
            pass

        try:
            await message.guild.ban(
                message.author,
                reason="Escribió en canal restringido",
                delete_message_days=1
            )
        except Exception as e:
            print(f"Error al banear: {e}")

        return

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🟢")

bot.run(TOKEN)
