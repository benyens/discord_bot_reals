import discord
import random
from discord.ext import commands
import os 
import web_server    
import json
import asyncio
from discord import FFmpegPCMAudio
from discord import PCMVolumeTransformer
import nacl

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True  
intents.message_content = True

bot = commands.Bot(command_prefix="*", intents=intents)

# Lista de gifs
GIF_LIST = [
    "https://tenor.com/view/spongebob-squarepants-gay-rainbow-lgbt-pride-month-gif-6443547037069682625",
    "https://tenor.com/view/lgbtq-positivity-psychology-positivity-lgbtq-pride-gayz-gif-4617705310496116143",
    "https://tenor.com/view/twomenkissing-twoblackmenkissing-kissing-kiss-gaykiss-gif-22635642",
    "https://tenor.com/view/black-people-kissing-tongue-out-gif-13635213"
]

# Lista de nicks temporales
NICKS_TEMPORALES = [
    "🏳️‍🌈 Weko 🏳️‍🌈",
    "🏳️‍🌈 Wekereke 🏳️‍🌈",
    "🏳️‍🌈 Maricón 🏳️‍🌈",
    "🏳️‍🌈 Homosexual 🏳️‍🌈",
    "🏳️‍🌈 Muerde almohadas 🏳️‍🌈",
    "🏳️‍🌈 ComePollitas 🏳️‍🌈"
]

RANKING_FILE = "ranking.json"

# Cargar ranking desde archivo
def cargar_ranking():
    if not os.path.exists(RANKING_FILE):
        return {}
    with open(RANKING_FILE, "r") as f:
        return json.load(f)

# Guardar ranking en archivo
def guardar_ranking(ranking):
    with open(RANKING_FILE, "w") as f:
        json.dump(ranking, f, indent=4)

# Función para reproducir audio
async def meterse_y_reproducir_audio(voice_channel, audio_url):
    try:
        voice_client = await voice_channel.connect()
        source = FFmpegPCMAudio(audio_url, executable=".config/npm/node_global/lib/node_modules/ffmpeg-static/ffmpeg")
        voice_client.play(source)

        while voice_client.is_playing():
            await asyncio.sleep(0.5)

        await voice_client.disconnect()
        print("[AUDIO] Se desconectó correctamente")

    except Exception as e:
        print(f"[ERROR AUDIO] {e}")
        
# Seguimiento por canal
channel_tracking = {}

@bot.event
async def on_voice_state_update(member, before, after):
    # Cuando alguien entra a un canal de voz
    if after.channel and (not before.channel or before.channel != after.channel):
        channel = after.channel
        print(f"[JOIN] {member.display_name} entró a {channel.name} - Total: {len(channel.members)}")

        if len(channel.members) >= 3:
            print(f"[TRACKING STARTED] Canal '{channel.name}' tiene 3 o más personas.")
            channel_tracking[channel.id] = True

    # Cuando alguien sale de un canal
    if before.channel and (not after.channel or before.channel != after.channel):
        channel = before.channel
        print(f"[LEAVE] {member.display_name} salió de {channel.name} - Total: {len(channel.members) - 1}")

        # Verifica si el canal estaba siendo trackeado y ya no queda nadie
        if channel.id in channel_tracking and len(channel.members) == 0:
            print(f"[LAST OUT] {member.display_name} fue el último en salir del canal '{channel.name}'")

            # Evita ejecuciones múltiples
            del channel_tracking[channel.id]

            last_user = member
            random_gif = random.choice(GIF_LIST)

            text_channel = discord.utils.get(channel.guild.text_channels, name="general-freaky👅")

            # Cargar y actualizar ranking
            ranking = cargar_ranking()
            user_id = str(member.id)

            if user_id in ranking:
                ranking[user_id]["count"] += 1
            else:
                ranking[user_id] = {
                    "name": member.display_name,
                    "count": 1
                }

            guardar_ranking(ranking)
            print(f"[RANKING] {member.display_name} ahora tiene {ranking[user_id]['count']} puntos.")

            if text_channel:
                print(f"[SEND] Enviando mensaje a #{text_channel.name}")
                await text_channel.send(f"🏳️‍🌈 **{last_user.display_name}** 🏳️‍🌈 fue el último en salir del canal de voz...")
                await text_channel.send(random_gif)
            else:
                print("[ERROR] Canal 'general-freaky👅' no encontrado")

            # Cambiar apodo temporalmente
            original_nick = last_user.display_name
            nuevo_nick = random.choice(NICKS_TEMPORALES)

            try:
                await last_user.edit(nick=nuevo_nick)
                print(f"[NICK] Cambiado apodo de {original_nick} a {nuevo_nick}")

                await asyncio.sleep(3600)  # 1 hora
                await last_user.edit(nick=original_nick)
                print(f"[NICK] Apodo de {last_user.display_name} restaurado a {original_nick}")

            except discord.Forbidden:
                print("[ERROR] No tengo permisos para cambiar el apodo de ese usuario.")
            except Exception as e:
                print(f"[ERROR] Falló el cambio de apodo: {e}")

# Comando ping
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 ¡Estoy vivo!")

# Comando ranking
@bot.command()
async def ranking(ctx):
    ranking = cargar_ranking()

    if not ranking:
        await ctx.send("Todavía no hay nadie en el ranking 💤")
        return

    top = sorted(ranking.items(), key=lambda x: x[1]["count"], reverse=True)

    msg = "🏆 **Ranking de los más wekos** 🏳️‍🌈\n"
    for i, (user_id, data) in enumerate(top[:10], start=1):
        msg += f"{i}. **{data['name']}** - {data['count']} veces\n"

    await ctx.send(msg)

web_server.keep_alive()
bot.run(DISCORD_TOKEN)
