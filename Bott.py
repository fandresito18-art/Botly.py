import discord
from discord.ext import commands
import re
import unicodedata
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# 🔹 CARGAR VARIABLES
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
print("TOKEN:", TOKEN)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

PALABRAS = [
    "estafa","estafas","estafador","estafadora","estafadores","estafando","estafado","estafaron",
    "robo","robos","robar","robando","robaron","robado","asaltaron","asalto","asaltos","asaltante","asaltantes",
    "ladron","ladrones","ratero","rateros","delincuente","delincuentes",
    "scam","scammer","scammers","scameador","scameadores","scameando",
    "fraude","fraudes","fraudulento","fraudulenta","defraudar","defraudaron",
    "engano","enganos","enganar","enganaron","enganado","enganoso",
    "timo","timos","timador","timadores","trampa","trampas","falsos",
    "falsificacion","suplantacion","suplantaron","phishing",
    "hackeo","hackearon","piratas","ciberdelincuentes"
]

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

def palabra_a_regex(p):
    return r"\b" + r"[\W_]*".join(list(p)) + r"\w*\b"

PATRON_PALABRAS = re.compile(
    "|".join(palabra_a_regex(p) for p in PALABRAS),
    re.IGNORECASE
)

PATRON_LINKS = re.compile(
    r"(https?:\/\/|www\.|discord\.gg\/|discord\.com\/invite\/)",
    re.IGNORECASE
)

def guardar_log(usuario, mensaje, razon):
    ahora = datetime.now()

    log_entry = {
        "usuario": str(usuario),
        "mensaje": mensaje,
        "razon": razon,
        "hora": ahora.strftime("%H:%M:%S"),
        "fecha": ahora.strftime("%Y-%m-%d")
    }

    try:
        with open("logs.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(log_entry)

    with open("logs.json", "w") as f:
        json.dump(data[-100:], f, indent=4)

async def borrar(message, razon):
    try:
        guardar_log(message.author, message.content, razon)
        await message.delete()
        print(f"[BORRADO] {message.author} → {razon}: {message.content}")
    except discord.Forbidden:
        print("Sin permisos")
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f"Bot activo como {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.guild_permissions.manage_messages:
        return

    contenido_normalizado = normalizar(message.content)

    if PATRON_LINKS.search(message.content):
        await borrar(message, "Enlace detectado")
        return

    if PATRON_PALABRAS.search(contenido_normalizado):
        await borrar(message, "Palabra prohibida")
        return

    await bot.process_commands(message)

@bot.command()
async def logs(ctx):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.send("No tienes permisos")

    try:
        with open("logs.json", "r") as f:
            data = json.load(f)
    except:
        return await ctx.send("No hay logs aún")

    if not data:
        return await ctx.send("No hay logs")

    texto = ""

    for log in data[-10:]:
        texto += f"{log['fecha']} {log['hora']} | {log['usuario']}\n"
        texto += f"[{log['razon']}] → {log['mensaje']}\n\n"

    await ctx.send(f"```{texto}```")

bot.run(TOKEN)
