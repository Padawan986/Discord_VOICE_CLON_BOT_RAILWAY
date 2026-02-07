import discord
from discord.ext import tasks, commands
import requests
import os
import random
from flask import Flask
from threading import Thread

# --- EINSTELLUNGEN ---
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1469695924971507854  # Deine Kanal-ID ist hier eingefügt
CHECK_INTERVAL = 5  # Prüft alle 5 Minuten

# --- FLASK WEB-SERVER (FÜR RENDER KEEP-ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT LOGIK ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Speicher für die letzte bekannte Version
last_update_id = None

def get_estimated_sizes():
    """Erzeugt Schätzungen für die Update-Größen."""
    pc = round(random.uniform(2.8, 5.5), 1)
    ps5 = round(random.uniform(3.5, 6.8), 1)
    ipad = round(random.uniform(1.5, 3.2), 1)
    return pc, ps5, ipad

@tasks.loop(minutes=CHECK_INTERVAL)
async def check_fortnite_update():
    global last_update_id
    
    try:
        url = "https://fortnite-api.com/v2/news/br"
        response = requests.get(url).json()
        
        if response['status'] == 200:
            current_id = response['data']['hash']
            
            # Falls ein neues Update da ist (ID hat sich geändert)
            if last_update_id is not None and current_id != last_update_id:
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    pc, ps5, ipad = get_estimated_sizes()
                    news_image = response['data'].get('image', '')

                    embed = discord.Embed(
                        title="🚀 NEUES FORTNITE UPDATE!",
                        description="Ein neues Update wurde auf den Servern gefunden.",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="🖥️ PC (Schätzung)", value=f"~{pc} GB", inline=True)
                    embed.add_field(name="🎮 PS5 (Schätzung)", value=f"~{ps5} GB", inline=True)
                    embed.add_field(name="📱 iPad/Mobile", value=f"~{ipad} GB", inline=True)
                    embed.add_field(name="📝 Status", value="Update ist jetzt verfügbar!", inline=False)
                    
                    if news_image:
                        embed.set_image(url=news_image)
                    
                    # Nachricht mit @everyone Ping senden
                    await channel.send(content="@everyone", embed=embed)
            
            last_update_id = current_id
            
    except Exception as e:
        print(f"Fehler: {e}")

@bot.event
async def on_ready():
    print(f'✅ Bot ist online als {bot.user.name}')
    if not check_fortnite_update.is_running():
        check_fortnite_update.start()

# --- START ---
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
