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
    url = "https://dxheat.com/dxc/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Fehler beim Abruf: HTTP {resp.status}")
                return []
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")

            spots = []
            spot_divs = soup.find_all("div", class_="dxspot")
            if not spot_divs:
                print("Keine DX-Spots gefunden auf der Seite.")
                return []

            for div in spot_divs:
                freq = div.find("span", class_="freq")
                mode = div.find("span", class_="mode")
                call = div.find("span", class_="call")
                spotter = div.find("span", class_="spotter")
                time_str = div.find("span", class_="time")

                if not (freq and mode and call and spotter and time_str):
                    continue

                spots.append({
                    "freq": freq.text.strip(),
                    "mode": mode.text.strip(),
                    "call": call.text.strip(),
                    "spotter": spotter.text.strip(),
                    "time": time_str.text.strip()
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


client.run(DISCORD_TOKEN)

