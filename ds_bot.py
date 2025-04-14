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

# Función para meterse en un canal y reproducir audio
async def meterse_y_reproducir_audio(voice_channel, audio_url):
    try:
        voice_client = await voice_channel.connect()

        # Usa el path local al ejecutable descargado
        source = FFmpegPCMAudio(audio_url, executable=".config/npm/node_global/lib/node_modules/ffmpeg-static/ffmpeg")

        voice_client.play(source)

        while voice_client.is_playing():
            await asyncio.sleep(0.5)

        await voice_client.disconnect()
        print("[AUDIO] Se desconectó correctamente")

    except Exception as e:
        print(f"[ERROR AUDIO] {e}")
        
# Diccionario para guardar seguimiento
channel_tracking = {}

@bot.event
async def on_voice_state_update(member, before, after):
    # Cuando alguien entra a un canal de voz
    if after.channel and (not before.channel or before.channel != after.channel):
        channel = after.channel
        print(f"[JOIN] {member.display_name} entró a {channel.name} - Total:                     {len(channel.members)}")

        if len(channel.members) >= 3:
            print(f"[TRACKING STARTED] Canal '{channel.name}' tiene 3 o más personas.")
            channel_tracking[channel.id] = {
                "members": set(m.id for m in channel.members),
                "last_member": None
            }
            
        # --- MODO CAÓTICO RANDOM DE AUDIO ---
        #if len(channel.members) >= 2 and not channel.guild.voice_client:
        #    probabilidad = 69
        #    print(f"[CHECK CAÓTICO] {len(channel.members)} personas en {channel.name} - Chance: {probabilidad}/500")

        #    if probabilidad == 69:  # El número mágico
        #        print(f"[ACTIVADO] 🎲 Entrando al canal {channel.name} con audio misterioso...")
        #        await meterse_y_reproducir_audio(channel, "callate-perkin.mp3")

    # Cuando alguien sale o cambia de canal
    if before.channel and (not after.channel or before.channel != after.channel):
        channel = before.channel
        print(f"[LEAVE] {member.display_name} salió de {channel.name} - Total:               {len(channel.members) - 1}")

        if channel.id in channel_tracking:
            tracking = channel_tracking[channel.id]
            tracking["members"].discard(member.id)
            tracking["last_member"] = member
            print(f"[UPDATE] {member.display_name} eliminado de tracking. Quedan: {len(tracking['members'])}")

            if len(tracking["members"]) == 0:
                print(f"[LAST OUT] {member.display_name} fue el último en salir del canal '{channel.name}'")

                last_user = tracking["last_member"]
                random_gif = random.choice(GIF_LIST)

                text_channel = discord.utils.get(channel.guild.text_channels,                             name="general-freaky👅")

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
                print(f"[RANKING] {member.display_name} ahora tiene {ranking[user_id] ['count']} puntos.")
                if text_channel:
                    print(f"[SEND] Enviando mensaje a #{text_channel.name}")
                    await text_channel.send(f"🏳️‍🌈 **{last_user.display_name}** 🏳️‍🌈 fue el último en salir del canal de voz...")
                    await text_channel.send(random_gif)
                else:
                    print("[ERROR] Canal 'general-freaky👅' no encontrado")

                # Guardar el nick original
                original_nick = last_user.display_name
                nuevo_nick = random.choice(NICKS_TEMPORALES)

                try:
                    await last_user.edit(nick=nuevo_nick)
                    print(f"[NICK] Cambiado apodo de {original_nick} a {nuevo_nick}")

                    # Espera 5 minutos y lo cambia de vuelta
                    await asyncio.sleep(3600)
                    await last_user.edit(nick=original_nick)
                    print(f"[NICK] Apodo de {last_user.display_name} restaurado a {original_nick}")

                except discord.Forbidden:
                    print("[ERROR] No tengo permisos para cambiar el apodo de ese usuario.")
                except Exception as e:
                    print(f"[ERROR] Falló el cambio de apodo: {e}")
                    


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 ¡Estoy vivo!")

@bot.command()
async def ranking(ctx):
    ranking = cargar_ranking()

    if not ranking:
        await ctx.send("Todavía no hay nadie en el ranking 💤")
        return

    # Ordenar por cantidad
    top = sorted(ranking.items(), key=lambda x: x[1]["count"], reverse=True)

    msg = "🏆 **Ranking de los más wekos** 🏳️‍🌈\n"
    for i, (user_id, data) in enumerate(top[:10], start=1):
        msg += f"{i}. **{data['name']}** - {data['count']} veces\n"

    await ctx.send(msg)
    
web_server.keep_alive()
bot.run(DISCORD_TOKEN)
