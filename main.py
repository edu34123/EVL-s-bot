import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import aiosqlite
import asyncio

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
TICKET_CHANNEL_ID = int(get_env_var('TICKET_CHANNEL_ID', 1392745580484231260))

INVITE_ROLES = {
    1: int(get_env_var('INVITE_ROLE_1_ID', 1392731553221578843)),
    3: int(get_env_var('INVITE_ROLE_3_ID', 1392731553624363058)),
    5: int(get_env_var('INVITE_ROLE_5_ID', 1392731554362425445)),
    10: int(get_env_var('INVITE_ROLE_10_ID', 1392731555188969613)),
    50: int(get_env_var('INVITE_ROLE_50_ID', 1392731615632818286)),
    100: int(get_env_var('INVITE_ROLE_100_ID', 1392731616060772424))
}

# VIEW CORRETTA PER I PULSANTI TICKET
class TicketCreationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🤝 Partnership", style=discord.ButtonStyle.primary, custom_id="auto_ticket_partnership")
    async def partnership_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_with_language(interaction, "partnership")
    
    @discord.ui.button(label="🛠️ Supporto", style=discord.ButtonStyle.secondary, custom_id="auto_ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_with_language(interaction, "support")
    
    async def create_ticket_with_language(self, interaction: discord.Interaction, ticket_type: str):
        """Crea ticket determinando automaticamente la lingua"""
        try:
            # Cerca i cog ticket
            cog_ita = interaction.client.get_cog('TicketSystemITA')
            cog_eng = interaction.client.get_cog('TicketSystemENG')
            
            print(f"🔍 Cog trovati: ITA={cog_ita is not None}, ENG={cog_eng is not None}")
            
            if not cog_ita and not cog_eng:
                await interaction.response.send_message("❌ Nessun sistema ticket caricato. Usa /debug_tickets per verificare.", ephemeral=True)
                return
            
            # Determina la lingua in base ai ruoli
            ita_role_id = 1402668379533348944
            eng_role_id = 1402668928890568785
            
            ita_role = interaction.guild.get_role(ita_role_id)
            eng_role = interaction.guild.get_role(eng_role_id)
            
            user_roles = [role.id for role in interaction.user.roles]
            
            # Logica di determinazione lingua
            if ita_role and ita_role.id in user_roles and cog_ita:
                print(f"🎯 Creazione ticket ITALIANO per {interaction.user.display_name}")
                await cog_ita.create_ticket(interaction, ticket_type)
            elif cog_eng:
                print(f"🎯 Creazione ticket INGLESE per {interaction.user.display_name}")
                await cog_eng.create_ticket(interaction, ticket_type)
            elif cog_ita:  # Fallback su italiano se inglese non disponibile
                print(f"🎯 Creazione ticket ITALIANO (fallback) per {interaction.user.display_name}")
                await cog_ita.create_ticket(interaction, ticket_type)
            else:
                await interaction.response.send_message("❌ Impossibile creare il ticket. Contatta l'admin.", ephemeral=True)
                
        except Exception as e:
            error_msg = f"❌ Errore creazione ticket: {str(e)}"
            print(error_msg)
            await interaction.response.send_message(error_msg, ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='>', intents=intents, help_command=None)
        self.ticket_channel_id = TICKET_CHANNEL_ID

    async def setup_hook(self):
        # DEBUG: mostra struttura file
        print("=== STRUTTURA FILE ===")
        try:
            items = os.listdir('.')
            for item in items:
                print(f"📁 {item}")
                
                if os.path.isdir(item):
                    try:
                        subitems = os.listdir(item)
                        for subitem in subitems:
                            print(f"  📄 {subitem}")
                    except Exception as e:
                        print(f"  ❌ Errore leggendo {item}: {e}")
        except Exception as e:
            print(f"❌ Errore lista file: {e}")
        
        # Prova entrambi i nomi della cartella (Cogs/cogs)
        cogs_paths = ['./Cogs', './cogs']
        cogs_loaded = False
        
        for cogs_path in cogs_paths:
            if os.path.exists(cogs_path):
                print(f"✅ Cartella {cogs_path} trovata!")
                for filename in os.listdir(cogs_path):
                    if filename.endswith('.py') and filename != '__init__.py':
                        try:
                            cog_name = f"{cogs_path[2:]}.{filename[:-3]}"
                            await self.load_extension(cog_name)
                            print(f"✅ Caricato: {cog_name}")
                            cogs_loaded = True
                        except Exception as e:
                            print(f"❌ Errore caricamento {filename}: {e}")
                break
        
        if not cogs_loaded:
            print("❌ Nessun cog caricato! Provo a caricare manualmente...")
            cog_names = ['fun', 'verification', 'partnership', 'moderation', 'leveling', 'invite_tracker', 'klubs', 'tickets']
            for cog_name in cog_names:
                try:
                    await self.load_extension(cog_name)
                    print(f"✅ Caricato: {cog_name}")
                except Exception as e:
                    print(f"❌ Errore {cog_name}: {e}")
        
        # VERIFICA COG TICKET
        print("\n🔍 VERIFICA COG TICKET:")
        cog_ita = self.get_cog('TicketSystemITA')
        cog_eng = self.get_cog('TicketSystemENG')
        print(f"   TicketSystemITA: {'✅' if cog_ita else '❌'}")
        print(f"   TicketSystemENG: {'✅' if cog_eng else '❌'}")
        
        # AGGIUNGI VIEW PERSISTENTE
        self.add_view(TicketCreationView())
        print("✅ View persistente aggiunta!")
        
        # Inizializza il database
        await self.init_db()
        
        # Sincronizza i comandi slash
        try:
            synced = await self.tree.sync()
            print(f"✅ Sincronizzati {len(synced)} comandi slash!")
            
            for cmd in synced:
                print(f"   - /{cmd.name}")
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

    async def setup_ticket_messages(self):
        """Invia automaticamente i messaggi dei ticket quando il bot si avvia"""
        print("🔄 Setup automatico messaggi ticket...")
        
        for guild in self.guilds:
            try:
                channel = guild.get_channel(self.ticket_channel_id)
                if not channel:
                    print(f"❌ Canale ticket non trovato nel server {guild.name}")
                    continue
                
                print(f"✅ Trovato canale ticket: #{channel.name} in {guild.name}")
                
                # Pulisci i vecchi messaggi del bot
                try:
                    async for message in channel.history(limit=20):
                        if message.author == self.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    print(f"🧹 Pulizia completata in #{channel.name}")
                except Exception as e:
                    print(f"⚠️ Errore durante la pulizia: {e}")
                
                await asyncio.sleep(2)
                
                # EMBED ITALIANO
                embed_ita = discord.Embed(
                    title="🎫 SISTEMA TICKET - ITALIANO 🇮🇹",
                    color=0x00ff00,
                    description="**Apri un ticket per richiedere assistenza o partnership!**"
                )
                
                embed_ita.add_field(
                    name="📋 Tipi di Ticket Disponibili",
                    value="**🤝 Partnership** - Per collaborazioni e partnership\n**🛠️ Supporto** - Per assistenza e problemi tecnici",
                    inline=False
                )
                
                embed_ita.add_field(
                    name="📜 Regole Ticket",
                    value="• Non taggare lo staff, verranno automaticamente notificati\n• Il ticket verrà chiuso dopo 24h di inattività\n• Sii chiaro e conciso nella tua richiesta\n• Rispetta lo staff e le sue decisioni",
                    inline=False
                )
                
                # EMBED INGLESE
                embed_eng = discord.Embed(
                    title="🎫 TICKET SYSTEM - ENGLISH 🇬🇧",
                    color=0x0099ff,
                    description="**Open a ticket to request assistance or partnership!**"
                )
                
                embed_eng.add_field(
                    name="📋 Available Ticket Types",
                    value="**🤝 Partnership** - For collaborations and partnerships\n**🛠️ Support** - For assistance and technical issues",
                    inline=False
                )
                
                embed_eng.add_field(
                    name="📜 Ticket Rules",
                    value="• Don't ping staff, they will be automatically notified\n• Ticket will be closed after 24h of inactivity\n• Be clear and concise in your request\n• Respect staff and their decisions",
                    inline=False
                )
                
                view = TicketCreationView()
                
                # Invia i messaggi
                await channel.send(embed=embed_ita, view=view)
                await channel.send(embed=embed_eng, view=view)
                
                print(f"✅ Messaggi ticket inviati in #{channel.name}")
                
            except Exception as e:
                print(f"❌ Errore durante l'invio dei messaggi ticket in {guild.name}: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ {bot.user} è online!')
    print(f'✅ ID Bot: {bot.user.id}')
    
    commands_count = len(bot.tree.get_commands())
    print(f'✅ Comandi registrati nel bot: {commands_count}')
    
    # VERIFICA FINALE COG TICKET
    cog_ita = bot.get_cog('TicketSystemITA')
    cog_eng = bot.get_cog('TicketSystemENG')
    print(f"🔍 TicketSystemITA: {'✅ CARICATO' if cog_ita else '❌ MANCANTE'}")
    print(f"🔍 TicketSystemENG: {'✅ CARICATO' if cog_eng else '❌ MANCANTE'}")
    
    # Aspetta che tutto sia pronto, poi invia i messaggi ticket
    await asyncio.sleep(5)
    await bot.setup_ticket_messages()
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="My Community and helping you with /help 👀"))

# Comando per risincronizzare manualmente
@bot.tree.command(name="sync", description="Risincronizza i comandi (solo admin)")
async def sync(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        try:
            synced = await bot.tree.sync()
            await interaction.response.send_message(f"✅ Sincronizzati {len(synced)} comandi!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Non hai i permessi per questo comando!", ephemeral=True)

# Comando per re-inviare i messaggi ticket
@bot.tree.command(name="setup_tickets", description="Re-invia i messaggi dei ticket (Admin)")
async def setup_tickets_cmd(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.defer(ephemeral=True)
        await bot.setup_ticket_messages()
        await interaction.followup.send("✅ Messaggi ticket re-inviati!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Non hai i permessi per questo comando!", ephemeral=True)

# Comando debug per verificare i cog
@bot.tree.command(name="debug_tickets", description="Debug sistema ticket (Admin)")
async def debug_tickets(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="🔍 DEBUG SISTEMA TICKET", color=0x0099ff)
        
        cog_ita = interaction.client.get_cog('TicketSystemITA')
        cog_eng = interaction.client.get_cog('TicketSystemENG')
        
        embed.add_field(
            name="Stato Cog", 
            value=f"**TicketSystemITA**: {'✅ CARICATO' if cog_ita else '❌ MANCANTE'}\n**TicketSystemENG**: {'✅ CARICATO' if cog_eng else '❌ MANCANTE'}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("❌ Non hai i permessi!", ephemeral=True)

@bot.tree.command(name="help", description="Mostra tutti i comandi disponibili")
async def help_command(interaction: discord.Interaction):
    commands_list = []
    for command in bot.tree.get_commands():
        commands_list.append(f"**/{command.name}** - {command.description}")
    
    embed = discord.Embed(title="🤖 Comandi di EVL's Bot", color=0x00ff00)
    embed.description = "\n".join(commands_list) if commands_list else "Nessun comando caricato 😢\nUsa `/sync` per aggiornare i comandi (solo admin)"
    embed.set_footer(text="EVL's Community Bot")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("✅ Token Discord trovato, avvio bot...")
        bot.run(token)
    else:
        print("❌ Token Discord non trovato!")
