import os
import socket
import discord
import asyncio

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN ist nicht gesetzt!")
if not DISCORD_CHANNEL_ID:
    raise ValueError("DISCORD_CHANNEL_ID ist nicht gesetzt!")

CHANNEL_ID = int(DISCORD_CHANNEL_ID)
client = discord.Client(intents=discord.Intents.default())

async def dx_listener():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Discord-Kanal nicht gefunden.")
        return

    s = socket.socket()
    s.connect(("cluster.dxde.net", 8000))
    s.send(b"\n")  # Login (leer lassen)

    print("✅ Verbunden mit DX Cluster.")

    while True:
        try:
            data = s.recv(4096).decode("utf-8", errors="ignore")
            lines = data.strip().split("\n")
            for line in lines:
                if "DX de" in line:
                    await channel.send(f"📡 `{line.strip()}`")
        except Exception as e:
            print(f"Fehler: {e}")
            await asyncio.sleep(5)

@client.event
async def on_ready():
    print(f"✅ Discord-Bot läuft als {client.user}")
    client.loop.create_task(dx_listener())

client.run(DISCORD_TOKEN)
