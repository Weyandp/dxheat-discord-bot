import os
import discord
import asyncio
import aiohttp
from bs4 import BeautifulSoup

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN ist nicht gesetzt!")
if not DISCORD_CHANNEL_ID:
    raise ValueError("DISCORD_CHANNEL_ID ist nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
client = discord.Client(intents=discord.Intents.default())

last_spots = set()  # Zum Duplikatsschutz

async def fetch_dx_spots():
    url = "https://www.qrz.com/dxcluster"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Fehler beim Abruf: HTTP {resp.status}")
                return []
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")

            table = soup.find("table")
            if not table:
                print("Keine Tabelle mit DX-Spots gefunden.")
                return []

            spots = []
            rows = table.find_all("tr")[1:]  # Header überspringen

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                spotter = cols[0].text.strip()
                frequency = cols[1].text.strip()
                mode = cols[2].text.strip()
                callsign = cols[3].text.strip()
                time = cols[4].text.strip()

                spots.append({
                    "spotter": spotter,
                    "frequency": frequency,
                    "mode": mode,
                    "callsign": callsign,
                    "time": time
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
            identifier = f"{spot['frequency']}-{spot['callsign']}-{spot['time']}"
            if identifier not in last_spots:
                new_spots.append(spot)
                last_spots.add(identifier)

        for spot in new_spots:
            message = (
                f"📡 **{spot['frequency']}** | {spot['mode']}\n"
                f"📞 {spot['callsign']} → {spot['spotter']}\n"
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
