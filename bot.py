import os
import discord
import aiohttp
import asyncio
from datetime import datetime
import pytz

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

# Zeitumwandlung: UTC -> Europe/Berlin (MEZ/MESZ)
def utc_to_german(utc_time_str: str) -> str:
    try:
        utc = pytz.utc
        german_tz = pytz.timezone("Europe/Berlin")
        utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
        utc_dt = utc.localize(utc_dt)
        german_dt = utc_dt.astimezone(german_tz)
        return german_dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception as e:
        print(f"Fehler bei Zeitumwandlung: {e}")
        return "Zeit unbekannt"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

API_URL = "https://web.cluster.iz3mez.it/spots.json"  # Beispiel API-URL (anpassen, falls nötig)
SPOT_LIMIT = 5
POST_INTERVAL = 30  # Sekunden

@client.event
async def on_ready():
    print(f"Bot läuft als {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Kanal nicht gefunden!")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(API_URL) as resp:
                    if resp.status != 200:
                        print(f"Fehler beim Abruf der Spots: HTTP {resp.status}")
                        await asyncio.sleep(POST_INTERVAL)
                        continue

                    data = await resp.json()

                    spots = data.get("spots", [])
                    if not spots:
                        print("Keine Spots gefunden.")
                        await asyncio.sleep(POST_INTERVAL)
                        continue

                    # Nur die letzten SPOT_LIMIT Spots
                    for spot in spots[:SPOT_LIMIT]:
                        call = spot.get("call", "Unbekannt")
                        freq = spot.get("freq", "Unbekannt")
                        band = spot.get("band", "Unbekannt")
                        spotter = spot.get("spotter", "Unbekannt")
                        utc_time = spot.get("spot_datetime_utc") or spot.get("time") or None

                        if utc_time is None:
                            zeit = "Zeit unbekannt"
                        else:
                            zeit = utc_to_german(utc_time)

                        embed = discord.Embed(title=f"DX Spot: {call}", color=0x1E90FF)
                        embed.add_field(name="Frequenz", value=f"{freq} kHz", inline=True)
                        embed.add_field(name="Band", value=band, inline=True)
                        embed.add_field(name="Spotter", value=spotter, inline=True)
                        embed.add_field(name="Zeit (MEZ/MESZ)", value=zeit, inline=False)
                        embed.set_footer(text="Powered by Patrick Weyand")

                        await channel.send(embed=embed)

                await asyncio.sleep(POST_INTERVAL)

            except Exception as e:
                print(f"Fehler in der Hauptschleife: {e}")
                await asyncio.sleep(POST_INTERVAL)

client.run(DISCORD_TOKEN)
