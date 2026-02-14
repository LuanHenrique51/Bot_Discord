import discord
from discord.ext import commands
import wavelink
import os
import asyncio

TOKEN = os.getenv("TOKEN")
LAVALINK_URI = os.getenv("LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔥 CONECTAR NO LAVALINK CORRETAMENTE
@bot.event
async def on_ready():
    print("Bot iniciando conexão com Lavalink...")

    try:
        node = wavelink.Node(
            uri=LAVALINK_URI,
            password=LAVALINK_PASSWORD,
        )

        await wavelink.Pool.connect(client=bot, nodes=[node])

        print("✅ Lavalink conectado com sucesso!")
        print(f"Bot online como {bot.user}")

    except Exception as e:
        print("❌ Erro ao conectar no Lavalink:")
        print(e)

# 🔊 PLAY
@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Você precisa estar em um canal de voz.")

    # Garantir que o Lavalink está conectado
    if not wavelink.Pool.get_nodes():
        return await ctx.send("⚠️ Lavalink ainda não está conectado. Aguarde alguns segundos.")

    player: wavelink.Player = ctx.voice_client

    if not player:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    # Buscar música
    tracks = await wavelink.Playable.search(search)

    if not tracks:
        return await ctx.send("❌ Música não encontrada.")

    track = tracks[0]

    await player.play(track)

    await ctx.send(f"🎶 Tocando agora: **{track.title}**")

# ⏹ STOP
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹ Música parada.")

# ⏭ SKIP
@bot.command()
async def skip(ctx):
    player: wavelink.Player = ctx.voice_client
    if player and player.playing:
        await player.stop()
        await ctx.send("⏭ Música pulada.")

# ▶ PAUSE
@bot.command()
async def pause(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.pause(True)
        await ctx.send("⏸ Música pausada.")

# ▶ RESUME
@bot.command()
async def resume(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.pause(False)
        await ctx.send("▶ Música retomada.")

bot.run(TOKEN)