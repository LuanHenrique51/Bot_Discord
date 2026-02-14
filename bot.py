import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import wavelink

# =========================
# VARIÁVEIS
# =========================
TOKEN = os.getenv("TOKEN")
LAVALINK_URI = os.getenv("LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

# =========================
# FLASK (obrigatório para Web Service)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot está rodando!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# =========================
# DISCORD CONFIG
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# CONEXÃO LAVALINK (FIX FINAL)
# =========================
@bot.event
async def on_ready():
    await bot.wait_until_ready()

    try:
        node = wavelink.Node(
            uri=LAVALINK_URI,
            password=LAVALINK_PASSWORD,
            secure=True  # ESSENCIAL para Render
        )

        await wavelink.Pool.connect(client=bot, nodes=[node])

        print("✅ Lavalink conectado com sucesso!")
        print(f"🤖 Bot online como {bot.user}")

    except Exception as e:
        print("❌ ERRO REAL AO CONECTAR:")
        print(type(e).__name__, e)

# =========================
# COMANDO PLAY
# =========================
@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Você precisa estar em um canal de voz.")

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        player = await channel.connect(cls=wavelink.Player)
    else:
        player = ctx.voice_client

    tracks = await wavelink.Playable.search(search)

    if not tracks:
        return await ctx.send("Nenhuma música encontrada.")

    track = tracks[0]

    await player.play(track)
    await ctx.send(f"▶ Tocando: {track.title}")

# =========================
# COMANDO STOP
# =========================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹ Desconectado.")

bot.run(TOKEN)