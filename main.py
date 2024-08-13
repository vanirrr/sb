import os
import discord
from discord.ext import commands

bot =commands.Bot(command_prefix="!", intents=discord.Intents.all() , self_bot=True)

@bot.event
async def on_ready():
    print("Running.")

bot.run("OTI3OTY3ODYwODM4NDk4MzQ0.GtqBA3.BBb-BWPOc5tLKURwys66Wn6gkvNJLFzBeNVpaA", bot=False)