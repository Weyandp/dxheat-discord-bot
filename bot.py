import os
import discord
import asyncio
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def fetch_dxheat_spots():
    url = "https://dxheat.com/dxc/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Fehler beim Abrufen von DXHeat: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    spots = []
    for row in soup.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) >= 4:
            spot = {
                'callsign': columns[0].text.strip(),
                'frequency': columns[1].text.strip(),
                'time': columns[2].text.strip(),
                'grid': columns[3].text.strip(),
            }
            spots.append(spot)
    return spots

async def dxheat_task():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Fehler: Kanal mit ID {CHANNEL_ID} nicht gefunden!")
        return

    while not client.is_closed():
        spots = fetch_dxheat_spots()
        if not spots:
            print("Keine Spots gefunden oder Fehler beim Abruf.")
        else:
            for spot in spots:
                message = f"📡 **{spot['callsign']}** spotted on {spot['frequency']} MHz at {spot['time']} UTC, grid {spot['grid']}"
                try:
                    await channel.send(message)
                except Exception as e:
                    print(f"Fehler beim Senden der Nachricht: {e}")

        await asyncio.sleep(600)  # 10 Minuten warten

@client.event
async def on_ready():
    print(f"Bot ist online als {client.user}")

client.loop.create_task(dxheat_task())
client.run(DISCORD_TOKEN)
