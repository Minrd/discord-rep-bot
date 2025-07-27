import discord
from discord.ext import commands
from flask import Flask
import threading
import json
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Token bus iš aplinkos kintamojo

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "reputation.json"

# Inicijuojam tuščią rep žemėlapį
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    print(f"✅ Botas prisijungė kaip {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "+rep" in message.content.lower():
        data = load_data()
        user_id = str(message.author.id)
        data[user_id] = data.get(user_id, 0) + 1
        save_data(data)
        await message.channel.send(f"{message.author.mention} gavo +rep! 🎉 Dabar turi {data[user_id]} rep.")
    
    await bot.process_commands(message)

@bot.command()
async def rep(ctx, user: discord.User = None):
    """Rodo kiek rep turi vartotojas"""
    data = load_data()
    if user is None:
        user = ctx.author
    rep_count = data.get(str(user.id), 0)
    await ctx.send(f"{user.mention} turi {rep_count} rep!")

@bot.command()
async def totalrep(ctx):
    """Rodo kiek viso rep turi serveris"""
    data = load_data()
    total = sum(data.values())
    await ctx.send(f"Serverio rep suma: {total} 🌟")

# Flask dalis 24/7 Render palaikymui
app = Flask('')

@app.route('/')
def home():
    return "Botas veikia!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()
bot.run(TOKEN)
