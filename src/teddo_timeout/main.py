from datetime import timedelta
from typing import Any, Optional
import discord
from discord import app_commands
from discord.ext import commands
import json
import argparse

args = argparse.ArgumentParser()
args.add_argument('--token', help='Discord bot token')
inputs = args.parse_args()

TOKEN = inputs.token  


# Define intents
intents = discord.Intents.default()

# Create bot instance
bot = commands.Bot(command_prefix="/", intents=intents)


# Dictionary to store timeout configurations {guild_id: timeout_seconds}
timeout_config = {}

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

    load_config()  

def load_config():
    """Load timeout configuration from file."""
    global timeout_config
    try:
        with open("timeout_config.json", "r") as f:
            timeout_config = json.load(f)
    except FileNotFoundError:
        print("Configuration file not found, loading empty configuration.")
    except Exception as e:
        print(f"Failed to load configuration: {e}")

def save_config():
    """Save the current timeout configuration to file."""
    try:
        with open("timeout_config.json", "w") as f:
            json.dump(timeout_config, f)
    except Exception as e:
        print(f"Failed to save configuration: {e}")

@bot.tree.command(name="settimeout", description="Set the timeout duration for teddo2488 in the guild.")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_timeout(ctx, seconds: int):
    """Set the timeout duration for teddo2488 in the guild."""
    if seconds < 0:
        await ctx.response.send_message("Timeout duration must be a positive integer.")
        return
    guild_id = str(ctx.guild.id)  # Convert to string for JSON compatibility
    timeout_config[guild_id] = seconds
    save_config()
    await ctx.response.send_message(f"Timeout duration for teddo2488 set to {seconds} seconds.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.name == "teddo2488":
        guild_id = str(message.guild.id)
        timeout_duration = timeout_config.get(guild_id, 30)  # Default to 60 seconds if not configured
        if timeout_duration == 0:
            return

        try:
            await message.author.timeout(timedelta(seconds=timeout_duration))
            print(f'Timed out {message.author.name} for {timeout_duration} seconds.')
        except Exception as e:
            print(f"Error timing out {message.author.name}: {e}")
    

bot.run(TOKEN)

