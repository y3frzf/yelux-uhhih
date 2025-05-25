import discord
import requests
import asyncio
import os
from datetime import datetime
from discord.ext import commands

# No load_dotenv() — we get env vars directly from Railway environmen

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content

bot = commands.Bot(command_prefix=".", intents=intents)

last_version = None

def get_current_date():
    # Use Discord timestamp format for timezone-aware display
    return f"<t:{int(datetime.utcnow().timestamp())}:F>"

# 🔴 Auto update embed
async def send_update_embed(version):
    channel = bot.get_channel(CHANNEL_ID)
    embed = discord.Embed(
        title="🔴 Yelux has detected a new update",
        description="Yelux is unavailable for use right now",
        color=discord.Color.red()
    )
    embed.add_field(name="Version", value=f"{version}\n", inline=False)
    embed.add_field(name="Platform", value="Windows\n", inline=False)
    embed.add_field(name="Date", value=get_current_date(), inline=False)
    embed.set_footer(
        text="Yelux",
        icon_url="https://cdn.discordapp.com/attachments/1371597079763222580/1375181584419917984/40_20250521213808.jpg?ex=6830c127&is=682f6fa7&hm=0551a94d34cd9d94939612f19b0e69ef17f264cd6370c5c49f4ca0bfc4ab2450&"
    )
    await channel.send(embed=embed)

# 🟢 Manual push embed
async def send_updated_embed(version, channel):
    embed = discord.Embed(
        title="🟢 Yelux has been updated",
        description="Yelux is now available for use",
        color=discord.Color.green()
    )
    embed.add_field(name="Version", value=f"{version}\n", inline=False)
    embed.add_field(name="Date", value=get_current_date(), inline=False)
    embed.add_field(name="Platform", value="Windows\n", inline=False)
    embed.set_footer(
        text="Yelux",
        icon_url="https://cdn.discordapp.com/attachments/1371597079763222580/1375181584419917984/40_20250521213808.jpg?ex=6830c127&is=682f6fa7&hm=0551a94d34cd9d94939612f19b0e69ef17f264cd6370c5c49f4ca0bfc4ab2450&"
    )
    await channel.send(embed=embed)

# 🔁 Background check for updates
async def check_for_updates():
    global last_version
    await bot.wait_until_ready()

    while True:
        try:
            res = requests.get("https://clientsettings.roblox.com/v2/client-version/WindowsPlayer")
            data = res.json()
            version = data.get("clientVersionUpload")

            if version and version != last_version:
                await send_update_embed(version)
                last_version = version

        except Exception as e:
            print(f"[Error] {e}")

        await asyncio.sleep(300)  # Check every 5 minutes

# 🟢 Hidden .push command
@bot.command(name="push")
async def push_command(ctx):
    if ctx.channel.id == CHANNEL_ID:
        res = requests.get("https://clientsettings.roblox.com/v2/client-version/WindowsPlayer")
        data = res.json()
        version = data.get("clientVersionUpload")
        await send_updated_embed(version, ctx.channel)

@bot.event
async def on_ready():
    print(f"✅ Yelux is online as {bot.user}")
    bot.loop.create_task(check_for_updates())

bot.run(TOKEN)
