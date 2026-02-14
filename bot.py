import discord
from discord.ext import commands
import wavelink
import os

TOKEN = os.getenv("TOKEN")

LAVALINK_URI = os.getenv("LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=ints := intents)

@bot.event
async def on_ready():
    node = wavelink.Node(
        uri=LAVALINK_URI,
        password=LAVALINK_PASSWORD
    )
    await wavelink.Pool.connect(client=bot, nodes=[node])
    print(f"Bot online como {bot.user}")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Entre em um canal de voz.")

    player = ctx.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)

    tracks = await wavelink.Playable.search(search)

    if not tracks:
        return await ctx.send("Não encontrei essa música.")

    track = tracks[0]
    await player.play(track)

    await ctx.send(f"🎶 Tocando: {track.title}")

bot.run(TOKEN)
