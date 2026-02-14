import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import yt_dlp

# =========================
# VARIÁVEIS
# =========================
TOKEN = os.getenv("TOKEN")

# =========================
# FLASK (para Render Web Service free)
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
# YTDL CONFIG
# =========================
ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# =========================
# PLAY COMMAND
# =========================
@bot.command()
async def play(ctx, *, url: str):
    if not ctx.author.voice:
        return await ctx.send("Você precisa estar em um canal de voz.")

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        voice = await channel.connect()
    else:
        voice = ctx.voice_client

    await ctx.send("🔎 Procurando música...")

    try:
        info = ytdl.extract_info(url, download=False)
        url2 = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)

        voice.stop()
        await voice.play(source)

        await ctx.send(f"▶ Tocando: {info.get('title')}")

    except Exception as e:
        await ctx.send("❌ Erro ao tocar música.")
        print(e)

# =========================
# STOP COMMAND
# =========================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹ Desconectado.")

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 Bot online como {bot.user}")

bot.run(TOKEN)