import os
import discord
import aiohttp
import asyncio

# Discord Token und Channel ID als Umgebungsvariablen
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN ist nicht gesetzt!")
if not CHANNEL_ID:
    raise ValueError("DISCORD_CHANNEL_ID ist nicht gesetzt!")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Beispiel-API mit DX-Spots (anpassen falls nötig)
API_URL = "https://web.cluster.iz3mez.it/spots.json"

SPOT_LIMIT = 5
POST_INTERVAL = 30  # Sekunden

@client.event
async def on_ready():
    print(f"Bot läuft als {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("Discord-Kanal nicht gefunden!")
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

                    for spot in spots[:SPOT_LIMIT]:
                        call = spot.get("call", "Unbekannt")
                        freq = spot.get("freq", "Unbekannt")
                        band = spot.get("band", "Unbekannt")
                        spotter = spot.get("spotter", "Unbekannt")
                        spot_country = spot.get("spot_country", "Unbekannt")
                        spotter_country = spot.get("spotter_country", "Unbekannt")
                        utc_time = spot.get("spot_datetime_utc") or spot.get("time") or "Zeit unbekannt"

                        embed = discord.Embed(title=f"DX Spot: {call}", color=0x1E90FF)
                        embed.add_field(name="Frequenz", value=f"{freq} kHz", inline=True)
                        embed.add_field(name="Band", value=band, inline=True)
                        embed.add_field(name="Land (Spot)", value=spot_country, inline=True)
                        embed.add_field(name="Land (Spotter)", value=spotter_country, inline=True)
                        embed.add_field(name="Spotter", value=spotter, inline=True)
                        embed.add_field(name="Zeit (UTC)", value=utc_time, inline=False)
                        embed.set_footer(text="Powered by Patrick Weyand")

                        await channel.send(embed=embed)

                await asyncio.sleep(POST_INTERVAL)

            except Exception as e:
                print(f"Fehler in der Hauptschleife: {e}")
                await asyncio.sleep(POST_INTERVAL)

client.run(DISCORD_TOKEN)
