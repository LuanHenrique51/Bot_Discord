import discord
from discord.ext import commands
import wavelink
import os

TOKEN = os.getenv("TOKEN")
LAVALINK_URI = os.getenv("LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = {}

@bot.event
async def on_ready():
    node = wavelink.Node(
        uri=LAVALINK_URI,
        password=LAVALINK_PASSWORD
    )

    await wavelink.Pool.connect(client=bot, nodes=[node])
    print("✅ Lavalink conectado!")
    print(f"Bot online como {bot.user}")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Entre em um canal de voz.")

    player: wavelink.Player = ctx.voice_client

    if not player:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    tracks = await wavelink.Playable.search(search)

    if not tracks:
        return await ctx.send("Música não encontrada.")

    track = tracks[0]

    if player.playing:
        queue.setdefault(ctx.guild.id, []).append(track)
        return await ctx.send(f"📌 Adicionado à fila: {track.title}")

    await player.play(track)
    await ctx.send(f"🎶 Tocando: {track.title}")

@bot.command()
async def skip(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.stop()

@bot.command()
async def stop(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.disconnect()

@bot.command()
async def pause(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.pause(True)

@bot.command()
async def resume(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        await player.pause(False)

@bot.event
async def on_wavelink_track_end(payload):
    player = payload.player
    guild_id = player.guild.id

    if guild_id in queue and queue[guild_id]:
        next_track = queue[guild_id].pop(0)
        await player.play(next_track)

bot.run(TOKEN)