import os
import discord
import asyncio
import aiohttp
import csv
from io import StringIO

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN ist nicht gesetzt!")
if not DISCORD_CHANNEL_ID:
    raise ValueError("DISCORD_CHANNEL_ID ist nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_dxspots():
    # Beispiel-URL für CSV-Daten von DXSummit, hier mit Limit 5 (maximale Spots)
    url = "https://www.dxsummit.fi/api/v1/spots?limit=5&content_type=csv&as_file=true"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Fehler beim Abruf: HTTP {resp.status}")
                return []

            text = await resp.text()
            csvfile = StringIO(text)
            reader = csv.DictReader(csvfile)
            spots = [row for row in reader]
            return spots

async def dxsummit_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Discord-Channel nicht gefunden!")
        return

    while True:
        spots = await fetch_dxspots()
        if not spots:
            print("Keine Spots gefunden oder Abruf fehlgeschlagen.")
            await asyncio.sleep(30)
            continue

        for spot in spots:
            # Beispiel-Spalten (kann je nach CSV-Format variieren)
            # Typische Felder: spotter, frequency, mode, callsign, time
            callsign = spot.get("call", "N/A")
            frequency = spot.get("freq", "N/A")
            mode = spot.get("mode", "N/A")
            spotter = spot.get("spotter", "N/A")
            time = spot.get("time", "N/A")

            embed = discord.Embed(title=f"DX Spot: {callsign}", color=0x1abc9c)
            embed.add_field(name="Frequency", value=frequency, inline=True)
            embed.add_field(name="Mode", value=mode, inline=True)
            embed.add_field(name="Spotter", value=spotter, inline=True)
            embed.add_field(name="Time", value=time, inline=True)

            await channel.send(embed=embed)

        await asyncio.sleep(30)  # Alle 30 Sekunden neu abrufen

@client.event
async def on_ready():
    print(f"Bot läuft als {client.user}")
    client.loop.create_task(dxsummit_loop())

client.run(DISCORD_TOKEN)
