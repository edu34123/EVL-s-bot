import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiosqlite
async def setup_hook(self):
    # DEBUG: mostra struttura file
    print("=== STRUTTURA FILE ===")
    try:
        items = os.listdir('.')
        for item in items:
            print(f"📁 {item}")
    except Exception as e:
        print(f"❌ Errore lista file: {e}")
    
    # Carica i cog con gestione errori
    cog_files = ['verification', 'partnership', 'moderation', 'fun', 'leveling', 'invite_tracker']
    
    for cog_name in cog_files:
        try:
            await self.load_extension(f'Cogs.{cog_name}')
            print(f"✅ Caricato: {cog_name}")
        except Exception as e:
            print(f"❌ Errore {cog_name}: {e}")

load_dotenv()

# Configurazione con valori di default
def get_env_var(name, default=None):
    value = os.getenv(name)
    if value is None:
        print(f"⚠️ Variabile {name} non trovata, uso default: {default}")
        return default
    return value

# Usa valori di default se le variabili non esistono
VERIFIED_ROLE_ID = int(get_env_var('VERIFIED_ROLE_ID', 1392128530438951084))
UNVERIFIED_ROLE_ID = int(get_env_var('UNVERIFIED_ROLE_ID', 1392111556954685450))
PARTNERSHIP_CHANNEL_ID = int(get_env_var('PARTNERSHIP_CHANNEL_ID', 1411451850485403830))

INVITE_ROLES = {
    1: int(get_env_var('INVITE_ROLE_1_ID', 1392731553221578843)),
    3: int(get_env_var('INVITE_ROLE_3_ID', 1392731553624363058)),
    5: int(get_env_var('INVITE_ROLE_5_ID', 1392731554362425445)),
    10: int(get_env_var('INVITE_ROLE_10_ID', 1392731555188969613)),
    50: int(get_env_var('INVITE_ROLE_50_ID', 1392731615632818286)),
    100: int(get_env_var('INVITE_ROLE_100_ID', 1392731616060772424))
}

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='/', intents=intents, help_command=None)
    
    async def setup_hook(self):
        # DEBUG: mostra struttura file
        print("=== STRUTTURA FILE ===")
        try:
            items = os.listdir('.')
            for item in items:
                print(f"📁 {item}")
                
                # Se è una cartella, mostra contenuto
                if os.path.isdir(item):
                    try:
                        subitems = os.listdir(item)
                        for subitem in subitems:
                            print(f"  📄 {subitem}")
                    except Exception as e:
                        print(f"  ❌ Errore leggendo {item}: {e}")
        except Exception as e:
            print(f"❌ Errore lista file: {e}")
        
        # Carica tutti i cog con gestione errori
        cogs_path = './cogs'
        if os.path.exists(cogs_path):
            print("✅ Cartella cogs trovata!")
            for filename in os.listdir(cogs_path):
                if filename.endswith('.py') and filename != '__init__.py':
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"✅ Caricato: {filename}")
                    except Exception as e:
                        print(f"❌ Errore caricamento {filename}: {e}")
        else:
            print("❌ Cartella cogs non trovata!")
            # Prova a caricare i cog manualmente
            cog_names = ['fun', 'verification', 'partnership', 'moderation', 'leveling', 'invite_tracker']
            for cog_name in cog_names:
                try:
                    await self.load_extension(cog_name)
                    print(f"✅ Caricato: {cog_name}")
                except Exception as e:
                    print(f"❌ Errore {cog_name}: {e}")
        
        # Inizializza il database
        await self.init_db()
        
        # Sincronizza i comandi slash
        try:
            await self.tree.sync()
            print("✅ Comandi slash sincronizzati!")
        except Exception as e:
            print(f"❌ Errore sincronizzazione: {e}")

    async def init_db(self):
        try:
            async with aiosqlite.connect('database.db') as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS levels (
                        user_id INTEGER PRIMARY KEY,
                        guild_id INTEGER,
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1
                    )
                ''')
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS invites (
                        user_id INTEGER,
                        guild_id INTEGER,
                        invites_count INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, guild_id)
                    )
                ''')
                await db.commit()
            print("✅ Database inizializzato!")
        except Exception as e:
            print(f"❌ Errore database: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ {bot.user} è online!')
    print(f'✅ ID Bot: {bot.user.id}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("✅ Token Discord trovato, avvio bot...")
        bot.run(token)
    else:
        print("❌ Token Discord non trovato!")

