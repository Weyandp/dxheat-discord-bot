import os
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from callsignparser import Call

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
API_URL = "https://web.cluster.iz3mez.it/spots.json/"

if not DISCORD_TOKEN or not DISCORD_CHANNEL_ID:
    raise ValueError("Token oder Channel-ID nicht gesetzt!")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def format_utc_timestamp(ts):
    try:
        dt = datetime.utcfromtimestamp(int(ts))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(ts)

def get_country_from_callsign(callsign):
    try:
        parsed = Call(callsign)
        country = parsed.country
        return country if country else "unbekannt"
    except Exception:
        return "unbekannt"

async def fetch_spots(limit=10):
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status != 200:
                print("API Fehler:", resp.status)
                return []
            data = await resp.json()
            return data[:limit]

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot ist online als {bot.user}")

@bot.tree.command(name="dxspots", description="Zeigt die letzten 10 DX-Spots")
async def dxspots_command(interaction: discord.Interaction):
    await interaction.response.defer()
    spots = await fetch_spots(10)
    if not spots:
        await interaction.followup.send("Keine DX-Spots gefunden.")
        return

    for spot in spots:
        call = spot.get("spotted", "unbekannt")
        freq = spot.get("frequency", "unbekannt")
        band = spot.get("band", "unbekannt")
        spotter = spot.get("spotter", "unbekannt")
        timestamp = format_utc_timestamp(spot.get("timestamp", "unbekannt"))
        spotted_country = get_country_from_callsign(call)
        spotter_country = get_country_from_callsign(spotter)

        embed = discord.Embed(
            title=f"DX Spot: {call} ({spotted_country})",
            color=0x007acc
        )
        embed.add_field(name="Frequenz (kHz)", value=freq, inline=True)
        embed.add_field(name="Band", value=band, inline=True)
        embed.add_field(name="Spotter", value=f"{spotter} ({spotter_country})", inline=True)
        embed.add_field(name="Zeit (UTC)", value=timestamp, inline=False)
        embed.set_footer(text="Powered by Patrick Weyand")

        await interaction.followup.send(embed=embed)

bot.run(DISCORD_TOKEN)
