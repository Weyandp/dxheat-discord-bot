import os
import discord
import asyncio
import aiohttp

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
API_URL = "https://web.cluster.iz3mez.it/spots.json/"

if not DISCORD_TOKEN or not DISCORD_CHANNEL_ID:
    raise ValueError("Token oder Channel-ID nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
client = discord.Client(intents=discord.Intents.default())

async def fetch_spots():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status != 200:
                print("API Fehler:", resp.status)
                return []
            data = await resp.json()
            return data[:5]  # nur die letzten 5 Spots

async def spot_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Kanal nicht gefunden!")
        return

    while True:
        spots = await fetch_spots()
        if spots:
            for spot in spots:
                embed = discord.Embed(title=f"DX Spot: {spot['spotted']}", color=0x007acc)
                embed.add_field(name="Frequenz", value=spot["frequency"], inline=True)
                embed.add_field(name="Band", value=spot.get("band", ""), inline=True)
                embed.add_field(name="Spotter", value=spot["spotter"], inline=True)
                embed.add_field(name="Zeit (UTC)", value=spot["spot_datetime_utc"], inline=False)
                await channel.send(embed=embed)
        else:
            print("Keine Spots oder API nicht erreichbar.")
        await asyncio.sleep(30)  # alle 30 Sekunden prüfen

@client.event
async def on_ready():
    print(f"✅ Bot läuft als {client.user}")
    client.loop.create_task(spot_loop())

client.run(DISCORD_TOKEN)
