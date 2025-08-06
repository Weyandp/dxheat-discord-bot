import os
import discord
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timezone

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN ist nicht gesetzt!")
if not DISCORD_CHANNEL_ID:
    raise ValueError("DISCORD_CHANNEL_ID ist nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
client = discord.Client(intents=discord.Intents.default())

last_spots = set()  # Zum Duplikatenschutz

async def fetch_dx_spots():
    url = "https://dxheat.com/dxc/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Fehler beim Abruf: HTTP {resp.status}")
                return []
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")

            spots = []
            # dxheat benutzt Tabelle mit id="dxheat_spots_table"
            table = soup.find("table", id="dxheat_spots_table")
            if not table:
                print("Tabelle mit DX-Spots nicht gefunden.")
                return []

            rows = table.find_all("tr")[1:]  # Erste Zeile ist Header
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                freq = cols[0].text.strip()
                mode = cols[1].text.strip()
                call = cols[2].text.strip()
                spotter = cols[3].text.strip()
                time_str = cols[5].text.strip()

                spots.append({
                    "freq": freq,
                    "mode": mode,
                    "call": call,
                    "spotter": spotter,
                    "time": time_str
                })
            return spots

async def dxheat_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Discord-Channel nicht gefunden!")
        return

    global last_spots

    while True:
        spots = await fetch_dx_spots()
        if not spots:
            print("Keine Spots gefunden oder Abruf fehlgeschlagen.")
            await asyncio.sleep(30)
            continue

        new_spots = []
        for spot in spots:
            identifier = f"{spot['freq']}-{spot['call']}-{spot['time']}"
            if identifier not in last_spots:
                new_spots.append(spot)
                last_spots.add(identifier)

        for spot in new_spots:
            message = (
                f"📡 **{spot['freq']}** | {spot['mode']}\n"
                f"📞 {spot['call']} → {spot['spotter']}\n"
                f"⏰ {spot['time']}"
            )
            await channel.send(message)

        # Speichere nur die letzten 100 Spots, um Speicher zu sparen
        if len(last_spots) > 100:
            last_spots = set(list(last_spots)[-100:])

        await asyncio.sleep(30)  # alle 30 Sekunden abrufen

@client.event
async def on_ready():
    print(f"Bot läuft als {client.user}")
    client.loop.create_task(dxheat_loop())

client.run(DISCORD_TOKEN)

