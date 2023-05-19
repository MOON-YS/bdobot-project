from cmath import log
from distutils.sysconfig import PREFIX
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
load_dotenv()
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from pytz import timezone



PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

bot = commands.Bot(command_prefix = PREFIX, intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} cinnabd(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey, {interaction.user.mention}! This is a slash command!", ephemeral=True)

@bot.tree.command(name="say")
@app_commands.describe(thing_to_say = "What should I Say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
    await interaction.response.send_message(f"{interaction.user.mention} said: '{thing_to_say}'")
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")
