import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import wavelink

TOKEN = os.getenv("TOKEN")

# =========================
# FLASK (para manter ativo no Render)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot rodando!"

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
# LAVALINK CONFIG
# =========================
LAVALINK_URI = "https://SEU-LAVALINK.onrender.com"
LAVALINK_PASSWORD = "youshallnotpass"

@bot.event
async def on_ready():
    print(f"🤖 Bot online como {bot.user}")

    await wavelink.NodePool.create_node(
        bot=bot,
        uri=LAVALINK_URI,
        password=LAVALINK_PASSWORD
    )

# =========================
# PLAY
# =========================
@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Entre em um canal de voz primeiro.")

    channel = ctx.author.voice.channel

    if not ctx.voice_client:
        vc = await channel.connect(cls=wavelink.Player)
    else:
        vc = ctx.voice_client

    await ctx.send("🔎 Procurando...")

    tracks = await wavelink.YouTubeTrack.search(search)

    if not tracks:
        return await ctx.send("Nada encontrado.")

    track = tracks[0]

    await vc.play(track)

    await ctx.send(f"▶ Tocando: {track.title}")

# =========================
# STOP
# =========================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹ Desconectado.")

bot.run(TOKEN)