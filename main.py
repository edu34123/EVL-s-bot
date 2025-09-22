import os
import os
# Configurazione
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID'))
PARTNERSHIP_CHANNEL_ID = int(os.getenv('PARTNERSHIP_CHANNEL_ID'))
INVITE_ROLES = {
    1: int(os.getenv('INVITE_ROLE_1_ID')),
    3: int(os.getenv('INVITE_ROLE_3_ID')),
    5: int(os.getenv('INVITE_ROLE_5_ID')),
    10: int(os.getenv('INVITE_ROLE_10_ID')),
    50: int(os.getenv('INVITE_ROLE_50_ID')),
    100: int(os.getenv('INVITE_ROLE_100_ID'))
}
import discord # type: ignore
from discord.ext import commands # type: ignore
from dotenv import load_dotenv # type: ignore
import aiosqlite # type: ignore

load_dotenv()

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='/', intents=intents, help_command=None)
    
    async def setup_hook(self):
        # Carica tutti i cog
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        # Inizializza il database
        await self.init_db()
        
        # Sincronizza i comandi slash
        await self.tree.sync()
        print("Comandi slash sincronizzati!")
    
    async def init_db(self):
        async with aiosqlite.connect('database.db') as db:
            # Tabella per i livelli
            await db.execute('''
                CREATE TABLE IF NOT EXISTS levels (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1
                )
            ''')
            
            # Tabella per gli inviti
            await db.execute('''
                CREATE TABLE IF NOT EXISTS invites (
                    user_id INTEGER,
                    guild_id INTEGER,
                    invites_count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            await db.commit()

bot = MyBot()

@bot.event
async def on_ready():
    print(f'{bot.user} è online!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

@bot.tree.command(name="help", description="Mostra tutti i comandi disponibili")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Comandi del Bot", color=0x00ff00)
    
    embed.add_field(name="🎯 **Verifica**", value="`/verify` - Sistema di verifica", inline=False)
    embed.add_field(name="🤝 **Partnership**", value="`/partnership` - Crea una partnership", inline=False)
    embed.add_field(name="⚡ **Moderazione**", value="`/ban`, `/kick`, `/timeout`, `/clear`", inline=False)
    embed.add_field(name="🎮 **Divertimento**", value="`/meme`, `/quote`, `/8ball`, `/cat`", inline=False)
    embed.add_field(name="📊 **Livelli**", value="`/level`, `/leaderboard`", inline=False)
    embed.add_field(name="📨 **Inviti**", value="`/invites` - Controlla i tuoi inviti", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))