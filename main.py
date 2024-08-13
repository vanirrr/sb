import os
import discord
from discord.ext import commands

bot =commands.Bot(command_prefix="!", intents=discord.Intents.all() , self_bot=True)

@bot.event
async def on_ready():
    print("Running.")

bot.run("OTI3OTY3ODYwODM4NDk4MzQ0.GlSpYx.Ac4mAo2Oc3URHEVMglmhw-jWFFr7oh64oNIjZg", bot=False)
