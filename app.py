from flask import Flask
import threading
import os
import time
import asyncio
import discord
from discord.ext import commands

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 EVL's Bot is running!"

@app.route('/health')
def health():
    return "✅ Healthy"

async def run_discord_bot():
    """Avvia il bot Discord"""
    print("🚀 Importazione e avvio bot Discord...")
    
    # Importa main.py che contiene tutti i tuoi comandi
    from main import bot, VERIFIED_ROLE_ID, UNVERIFIED_ROLE_ID, PARTNERSHIP_CHANNEL_ID, INVITE_ROLES
    
    # Avvia il bot
    token = os.getenv('DISCORD_TOKEN')
    if token:
        await bot.start(token)
    else:
        print("❌ Token non trovato!")

def start_bot():
    """Wrapper per avviare il bot in un thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_discord_bot())
    except Exception as e:
        print(f"❌ Errore bot: {e}")
    finally:
        loop.close()

if __name__ == '__main__':
    # Avvia il bot in un thread separato
    print("🌐 Avvio server Flask...")
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Avvia Flask (processo principale)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
