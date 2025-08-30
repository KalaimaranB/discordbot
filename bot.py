# bot.py
import os
import asyncio
import pytz
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])  # put numeric channel id in Render env
TZ = pytz.timezone("America/Vancouver")     # change if you want another timezone

# Make sure pings are actually allowed
allowed_mentions = discord.AllowedMentions(everyone=True, roles=True, users=True)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, allowed_mentions=allowed_mentions)
scheduler = AsyncIOScheduler()

async def send_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            await channel.send("@everyone It's your scheduled reminder! 🚀")
            print("Message sent")
        except Exception as e:
            print("Failed to send:", e)
    else:
        print("Channel not found. Is the bot in the server and channel ID correct?")

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user} (guilds: {len(bot.guilds)})")
    if not scheduler.running:
        # 🔄 for testing: run send_message every 1 minute
        scheduler.add_job(send_message, "interval", minutes=1)
        scheduler.start()


# Simple HTTP endpoint so Render's Web Service detects a bound port
async def handle(request):
    return web.Response(text="OK - bot is running")

async def start_webserver_and_bot():
    # start webserver
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT env var
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server running on port {port}")

    # start discord bot (this blocks until bot stops)
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(start_webserver_and_bot())
    except KeyboardInterrupt:
        print("Shutting down")

