import os
import discord
from discord.ext import commands
import wavelink

TOKEN = os.getenv("TOKEN")
LAVALINK_URI = os.getenv("LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.wait_until_ready()

    try:
        nodes = [
            wavelink.Node(
                uri=LAVALINK_URI,
                password=LAVALINK_PASSWORD
            )
        ]

        await wavelink.Pool.connect(nodes=nodes, client=bot)

        print("✅ Lavalink conectado com sucesso!")
        print(f"🤖 Bot online como {bot.user}")

    except Exception as e:
        print("❌ ERRO AO CONECTAR NO LAVALINK:")
        print(repr(e))


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


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹ Desconectado.")


bot.run(TOKEN)