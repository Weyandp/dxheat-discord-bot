import os
import discord
import asyncio
import aiohttp
from datetime import datetime
import pytz

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
API_URL = "https://web.cluster.iz3mez.it/spots.json/"

if not DISCORD_TOKEN or not DISCORD_CHANNEL_ID:
    raise ValueError("DISCORD_TOKEN oder DISCORD_CHANNEL_ID ist nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
client = discord.Client(intents=discord.Intents.default())

# Umwandlung von UTC nach deutscher Zeit (automatisch Sommer-/Winterzeit)
def utc_to_german(utc_time_str):
    try:
        utc = pytz.utc
        german_tz = pytz.timezone("Europe/Berlin")
        utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
        utc_dt = utc.localize(utc_dt)
        german_dt = utc_dt.astimezone(german_tz)
        return german_dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return "Zeit unbekannt"

async def fetch_spots():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status != 200:
                print("API-Fehler:", resp.status)
                return []
            data = await resp.json()
            return data[:5]  # Nur die letzten 5 Spots

async def spot_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Discord-Kanal nicht gefunden!")
        return

    while True:
        spots = await fetch_spots()
        if not spots:
            print("⚠️ Keine Spots oder API nicht erreichbar.")
        else:
            for spot in spots:
                rufzeichen = spot.get("spotted", "Unbekannt")
                frequenz = spot.get("frequency", "Unbekannt")
                band = spot.get("band", "Unbekannt")
                spotter = spot.get("spotter", "Unbekannt")
                utc_zeit = spot.get("spot_datetime_utc") or spot.get("spot_time") or "Unbekannt"
                deutsche_zeit = utc_to_german(utc_zeit) if "Unbekannt" not in utc_zeit else "Zeit unbekannt"

                embed = discord.Embed(
                    title="📡 Neuer DX-Spot",
                    description="Ein neuer DX-Spot wurde gemeldet:",
                    color=0x3498db
                )
                embed.add_field(name="Rufzeichen", value=rufzeichen, inline=True)
                embed.add_field(name="Frequenz", value=frequenz, inline=True)
                embed.add_field(name="Band", value=band, inline=True)
                embed.add_field(name="Gesichtet von", value=spotter, inline=True)
                embed.add_field(name="Zeit (Deutschland)", value=deutsche_zeit, inline=False)
                embed.set_footer(text="Powered by Patrick Weyand • Daten via IZ3MEZ Cluster")

                await channel.send(embed=embed)

        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f"✅ Bot läuft als {client.user}")
    client.loop.create_task(spot_loop())

client.run(DISCORD_TOKEN)
