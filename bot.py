import os
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import requests
from bs4 import BeautifulSoup
import re

# ===== CONFIG DO BOT =====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== GENIUS TOKEN =====
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")
# ===== YT-DLP CONFIG =====
ytdl_options = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extractor_args': {
        'youtube': {
            'player_client': ['android'],
        }
    }
}

ffmpeg_options = {
    'before_options': (
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
        '-nostdin'
    ),
    'options': (
        '-vn '
        '-af "loudnorm=I=-16:TP=-1.5:LRA=11" '
        '-ac 2 '
        '-ar 48000 '
        '-b:a 192k'
    )
}

ytdl = yt_dlp.YoutubeDL(ytdl_options)

music_queue = {}
is_playing = {}

# ===== BUSCAR LETRA NO GENIUS =====
async def get_lyrics(title):
    try:
        headers = {
            "Authorization": f"Bearer {GENIUS_TOKEN}"
        }

        search_url = "https://api.genius.com/search"
        data = {"q": title}

        response = requests.get(search_url, headers=headers, params=data)
        json_data = response.json()

        hits = json_data["response"]["hits"]
        if not hits:
            return None, None, None

        song = hits[0]["result"]
        song_url = song["url"]
        artist = song["primary_artist"]["name"]
        cover = song["song_art_image_url"]

        page = requests.get(song_url)
        soup = BeautifulSoup(page.text, "html.parser")

        containers = soup.find_all("div", {"data-lyrics-container": "true"})
        if not containers:
            return None, None, None

        lyrics = ""

        for container in containers:
            for br in container.find_all("br"):
                br.replace_with("\n")
            lyrics += container.get_text() + "\n"

        lyrics = re.sub(r'\n{3,}', '\n\n', lyrics).strip()

        if len(lyrics) > 3500:
            lyrics = lyrics[:3500] + "\n\n... (letra cortada)"

        return lyrics, artist, cover

    except Exception as e:
        print(e)
        return None, None, None

# ===== TOCAR PRÓXIMA =====
async def play_next(ctx):
    guild_id = ctx.guild.id

    if music_queue[guild_id]:
        is_playing[guild_id] = True
        url, title = music_queue[guild_id].pop(0)

        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url, **ffmpeg_options),
            volume=0.8
        )

        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next(ctx), bot.loop
            )
        )

        await ctx.send(f"🎶 Tocando agora: **{title}**")

        lyrics, artist, cover = await get_lyrics(title)

        if lyrics:
            embed = discord.Embed(
                title=title,
                description=lyrics[:4000],
                color=0x1DB954
            )
            embed.set_author(name=artist)
            embed.set_thumbnail(url=cover)
            embed.set_footer(text="Letra via Genius")

            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Letra não encontrada.")

    else:
        is_playing[guild_id] = False

# ===== EVENTO =====
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# ===== PLAY =====
@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("❌ Entre em um canal de voz.")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    guild_id = ctx.guild.id
    music_queue.setdefault(guild_id, [])
    is_playing.setdefault(guild_id, False)

    try:
        info = ytdl.extract_info(search, download=False)

        if 'entries' in info:
            info = info['entries'][0]

        url = info['url']
        title = info['title']

        music_queue[guild_id].append((url, title))

        if not is_playing[guild_id]:
            await play_next(ctx)
        else:
            await ctx.send(f"📌 Adicionado à fila: **{title}**")

    except Exception as e:
        await ctx.send("❌ Erro ao tocar a música.")
        print(e)

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")
if __name__ == "__main__":
    bot.run(TOKEN)
