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

# VIEW PERSISTENTE PER I PULSANTI TICKET
class PersistentTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🤝 Partnership", style=discord.ButtonStyle.primary, custom_id="persistent_ticket_partnership")
    async def partnership_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Prova prima il modulo ticket italiano, poi inglese
        cog_ita = interaction.client.get_cog('TicketSystemITA')
        cog_eng = interaction.client.get_cog('TicketSystemENG')
        
        if cog_ita:
            await cog_ita.create_ticket(interaction, "partnership")
        elif cog_eng:
            await cog_eng.create_ticket(interaction, "partnership")
        else:
            await interaction.response.send_message("❌ Nessun sistema ticket caricato. Contatta l'admin.", ephemeral=True)
    
    @discord.ui.button(label="🛠️ Supporto", style=discord.ButtonStyle.secondary, custom_id="persistent_ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Prova prima il modulo ticket italiano, poi inglese
        cog_ita = interaction.client.get_cog('TicketSystemITA')
        cog_eng = interaction.client.get_cog('TicketSystemENG')
        
        if cog_ita:
            await cog_ita.create_ticket(interaction, "support")
        elif cog_eng:
            await cog_eng.create_ticket(interaction, "support")
        else:
            await interaction.response.send_message("❌ Nessun sistema ticket caricato. Contatta l'admin.", ephemeral=True)

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(command_prefix='>', intents=intents, help_command=None)
        self.ticket_channel_id = TICKET_CHANNEL_ID
        print(f"🎯 Canale ticket configurato: {self.ticket_channel_id}")

    async def setup_hook(self):
        print("=== CARICAMENTO MODULI TICKET ===")
        
        # LISTA DI TUTTI I MODULI TICKET CHE DEVI AVERE
        ticket_modules = [
            'cogs.tickets_ita',    # Modulo ticket italiano
            'cogs.tickets_eng',    # Modulo ticket inglese
            'cogs.tickets',        # Modulo ticket generico (backup)
            'tickets_ita',         # Nomi diretti
            'tickets_eng',
            'tickets'
        ]
        
        # AGGIUNGI ANCHE TUTTI GLI ALTRI COG
        all_modules = [
            'cogs.verification',
            'cogs.fun', 
            'cogs.partnership',
            'cogs.moderation',
            'cogs.leveling',
            'cogs.invite_tracker',
            'cogs.klubs'
        ] + ticket_modules
        
        print("🔄 Tentativo di caricamento moduli...")
        
        modules_loaded = []
        modules_failed = []
        
        for module_name in all_modules:
            try:
                await self.load_extension(module_name)
                modules_loaded.append(module_name)
                print(f"✅ Caricato: {module_name}")
            except Exception as e:
                modules_failed.append(f"{module_name}: {e}")
        
        print(f"\n📊 RIEPILOGO CARICAMENTO:")
        print(f"✅ Moduli caricati: {len(modules_loaded)}")
        print(f"❌ Moduli falliti: {len(modules_failed)}")
        
        if modules_loaded:
            print("📦 Moduli caricati con successo:")
            for module in modules_loaded:
                print(f"   - {module}")
        
        if modules_failed:
            print("⚠️ Moduli non caricati:")
            for error in modules_failed:
                print(f"   - {error}")
        
        # VERIFICA SPECIFICA DEI MODULI TICKET
        print("\n🎯 VERIFICA MODULI TICKET:")
        ticket_cogs = []
        for cog_name in ['TicketSystemITA', 'TicketSystemENG', 'TicketSystem']:
            cog = self.get_cog(cog_name)
            if cog:
                ticket_cogs.append(cog_name)
                print(f"✅ Trovato: {cog_name}")
            else:
                print(f"❌ Non trovato: {cog_name}")
        
        if not ticket_cogs:
            print("🚨 CRITICO: Nessun modulo ticket caricato!")
        else:
            print(f"✅ Moduli ticket attivi: {', '.join(ticket_cogs)}")
        
        # AGGIUNGI LA VIEW PERSISTENTE PER I TICKET
        self.add_view(PersistentTicketView())
        print("✅ View persistente ticket aggiunta!")
        
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
        print("🔄 Setup messaggi ticket...")
        
        for guild in self.guilds:
            try:
                channel = guild.get_channel(self.ticket_channel_id)
                if not channel:
                    print(f"❌ Canale ticket {self.ticket_channel_id} non trovato!")
                    return
                
                print(f"✅ Canale ticket: #{channel.name} (ID: {channel.id})")
                
                # Pulisci SOLO i messaggi ticket del bot
                try:
                    deleted_count = 0
                    async for message in channel.history(limit=30):
                        if message.author == self.user:
                            is_ticket_message = False
                            
                            # Controlla se è un messaggio ticket
                            if message.content and 'ticket' in message.content.lower():
                                is_ticket_message = True
                            for embed in message.embeds:
                                if embed.title and 'ticket' in embed.title.lower():
                                    is_ticket_message = True
                                    break
                            
                            if is_ticket_message:
                                await message.delete()
                                deleted_count += 1
                                await asyncio.sleep(0.5)
                    
                    print(f"🧹 Cancellati {deleted_count} messaggi ticket vecchi")
                    
                except Exception as e:
                    print(f"⚠️ Errore pulizia: {e}")
                
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
                
                # Usa la view persistente
                view = PersistentTicketView()
                
                # Invia i messaggi
                await channel.send(embed=embed_ita, view=view)
                await channel.send(embed=embed_eng, view=view)
                
                print("✅ Messaggi ticket inviati!")
                
            except Exception as e:
                print(f"❌ Errore: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ {bot.user} è online!')
    print(f'✅ ID Bot: {bot.user.id}')
    
    # VERIFICA DETTAGLIATA DEI MODULI TICKET
    print("\n🔍 STATO MODULI TICKET:")
    for cog_name in ['TicketSystemITA', 'TicketSystemENG', 'TicketSystem']:
        cog = bot.get_cog(cog_name)
        if cog:
            print(f"✅ {cog_name} - CARICATO")
        else:
            print(f"❌ {cog_name} - NON CARICATO")
    
    commands_count = len(bot.tree.get_commands())
    print(f'✅ Comandi registrati: {commands_count}')
    
    # Invio messaggi ticket (SICURO)
    await bot.setup_ticket_messages()
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="My Community and helping you with /help 👀"))

# Comando per verificare lo stato dei moduli
@bot.tree.command(name="ticket_status", description="Verifica lo stato dei moduli ticket (Admin)")
async def ticket_status(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        embed = discord.Embed(title="🔍 STATO MODULI TICKET", color=0x0099ff)
        
        status_text = ""
        for cog_name in ['TicketSystemITA', 'TicketSystemENG', 'TicketSystem']:
            cog = interaction.client.get_cog(cog_name)
            status = "✅ CARICATO" if cog else "❌ NON CARICATO"
            status_text += f"**{cog_name}**: {status}\n"
        
        embed.description = status_text
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("❌ Non hai i permessi!", ephemeral=True)

@bot.tree.command(name="setup_tickets", description="Re-invia i messaggi dei ticket (Admin)")
async def setup_tickets_cmd(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.defer(ephemeral=True)
        try:
            await bot.setup_ticket_messages()
            await interaction.followup.send("✅ Messaggi ticket re-inviati!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Errore: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Non hai i permessi!", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("✅ Token Discord trovato, avvio bot...")
        bot.run(token)
    else:
        print("❌ Token Discord non trovato!")
