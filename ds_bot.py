import discord
import random
from discord.ext import commands
import os 

token = "MTM2MTAxNDEwMjc0MjUzNjMxMw.GD6MDR.RrFcYhXdc3QmSl_w79WLJ966Bm63DcHjh76udY"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable not set.")

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)

# Lista de gifs
GIF_LIST = [
    "https://tenor.com/view/spongebob-squarepants-gay-rainbow-lgbt-pride-month-gif-6443547037069682625",
    "https://tenor.com/view/lgbtq-positivity-psychology-positivity-lgbtq-pride-gayz-gif-4617705310496116143",
    "https://tenor.com/view/twomenkissing-twoblackmenkissing-kissing-kiss-gaykiss-gif-22635642",
    "https://tenor.com/view/black-people-kissing-tongue-out-gif-13635213"
]

# Diccionario para guardar seguimiento
channel_tracking = {}

@bot.event
async def on_voice_state_update(member, before, after):
    # Se conecta a un canal
    if after.channel and (not before.channel or before.channel != after.channel):
        channel = after.channel
        if len(channel.members) >= 3:
            channel_tracking[channel.id] = {
                "members": set(m.id for m in channel.members),
                "last_member": None
            }

    # Se desconecta o cambia de canal
    if before.channel and (not after.channel or before.channel != after.channel):
        channel = before.channel
        if channel.id in channel_tracking:
            tracking = channel_tracking[channel.id]
            tracking["members"].discard(member.id)
            tracking["last_member"] = member

            if len(tracking["members"]) == 0:
                # Último en salir
                last_user = tracking["last_member"]
                random_gif = random.choice(GIF_LIST)

                text_channel = discord.utils.get(channel.guild.text_channels, name="general")  # o el canal que quieras
                if text_channel:
                    await text_channel.send(f"🏳️‍🌈 **{last_user.display_name}** 🏳️‍🌈 fue el último en salir...")
                    await text_channel.send(random_gif)

                del channel_tracking[channel.id]

bot.run(DISCORD_TOKEN)
