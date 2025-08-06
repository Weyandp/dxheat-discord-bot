import os
import discord
import asyncio
import aiohttp

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
API_URL = "https://web.cluster.iz3mez.it/spots.json/"

if not DISCORD_TOKEN or not DISCORD_CHANNEL_ID:
    raise ValueError("DISCORD_TOKEN oder DISCORD_CHANNEL_ID ist nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
client = discord.Client(intents=discord.Intents.default())

async def fetch_spots():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status != 200:
                print("API-Fehler:", resp.status)
                return []
            data = await resp.json()
            return data[:5]  # Maximal 5 aktuelle Spots

async def spot_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Discord-Kanal nicht gefunden!")
        return

    while True:
        spots = await fetch_spots()
        if not spots:
            print("Keine Spots oder API nicht erreichbar.")
        else:
            for spot in spots:
                title = spot.get("spotted", "unbekannt")
                frequency = spot.get("frequency", "unbekannt")
                band = spot.get("band", "unbekannt")
                spotter = spot.get("spotter", "unbekannt")
                # Zeit abrufen: bevorzugt spot_datetime_utc, sonst spot_time
                time_str = spot.get("spot_datetime_utc") or spot.get("spot_time") or "unbekannt"

                embed = discord.Embed(title=f"DX Spot: {title}", color=0x1abc9c)
                embed.add_field(name="Frequency", value=frequency, inline=True)
                embed.add_field(name="Band", value=band, inline=True)
                embed.add_field(name="Spotter", value=spotter, inline=True)
                embed.add_field(name="Zeit (UTC)", value=time_str, inline=False)
                await channel.send(embed=embed)

        await asyncio.sleep(30)

@client.event
async def on_ready():
    print(f"✅ Bot läuft als {client.user}")
    client.loop.create_task(spot_loop())

client.run(DISCORD_TOKEN)
