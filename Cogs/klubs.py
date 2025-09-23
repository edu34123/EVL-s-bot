import discord
from discord.ext import commands
import asyncio
import os

class Klubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.klubs = {}
        
        # Configurazione corretta
        self.ALLOWED_ROLE_IDS = [int(role_id.strip()) for role_id in os.getenv('KLUBS_ALLOWED_ROLES', '1402733312799412244,1311367694716633159,1407081522896572508,1394357096295956580').split(',')]
        self.KLUBS_CHANNEL_ID = int(os.getenv('KLUBS_CHANNEL_ID', '1402978154284453908'))
        
        print(f"✅ Configurazione Klubs caricata:")
        print(f"   - Ruoli autorizzati: {self.ALLOWED_ROLE_IDS}")
        print(f"   - Canale klubs: {self.KLUBS_CHANNEL_ID}")

    async def get_klubs_category(self, guild):
        """Crea o ottiene la categoria per i klub"""
        # Cerca una categoria esistente
        for category in guild.categories:
            if "klub" in category.name.lower() or "privati" in category.name.lower():
                return category
        
        # Crea una nuova categoria
        category = await guild.create_category("🎯 KLUBS", position=0)
        return category

    class Klub:
        def __init__(self, owner, voice_channel, text_channel, name):
            self.owner = owner
            self.voice_channel = voice_channel
            self.text_channel = text_channel
            self.name = name
            self.locked = False
            self.trusted_users = [owner]

    @commands.Cog.listener()
    async def on_ready(self):
        """Inizializza il sistema Klubs quando il bot è pronto"""
        print("✅ Sistema Klubs caricato!")
        print(f"✅ Bot è in {len(self.bot.guilds)} server")
        
        # Aspetta che il bot sia completamente pronto
        await asyncio.sleep(5)
        
        # Debug: mostra i server e canali
        for guild in self.bot.guilds:
            print(f"🔍 Server: {guild.name} (ID: {guild.id})")
            channel = guild.get_channel(self.KLUBS_CHANNEL_ID)
            if channel:
                print(f"✅ Canale klubs trovato: #{channel.name} (ID: {channel.id})")
                await self.setup_klubs_channel()
                return
            else:
                print(f"❌ Canale {self.KLUBS_CHANNEL_ID} non trovato in {guild.name}")
        
        print("⚠️ Canale klubs non trovato in nessun server.")

    async def setup_klubs_channel(self):
        """Configura il canale klubs"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.KLUBS_CHANNEL_ID)
            if channel:
                try:
                    print(f"🔄 Configuro il canale #{channel.name}...")
                    
                    # Pulisci i vecchi messaggi del bot
                    deleted_count = 0
                    async for message in channel.history(limit=50):
                        if message.author == self.bot.user:
                            await message.delete()
                            deleted_count += 1
                            await asyncio.sleep(0.5)  # Evita rate limit
                    
                    print(f"🗑️ Eliminati {deleted_count} vecchi messaggi")
                    await asyncio.sleep(2)
                    
                    await self.send_klubs_message(channel)
                    print(f"✅ Messaggio klubs inviato in #{channel.name}")
                    return
                except Exception as e:
                    print(f"❌ Errore configurazione canale klubs: {e}")
                    import traceback
                    traceback.print_exc()

    async def send_klubs_message(self, channel):
        """Crea il messaggio embed per i klubs"""
        try:
            # Verifica i permessi del bot
            permissions = channel.permissions_for(channel.guild.me)
            if not permissions.send_messages:
                print("❌ Il bot non ha permesso di inviare messaggi in questo canale")
                return
            if not permissions.embed_links:
                print("❌ Il bot non ha permesso di inviare embed in questo canale")
                return

            embed = discord.Embed(
                title="🎯 EChat APP - Klubs System",
                description="Sistema di vocali privati",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(
                name="Cosa sono i Klubs?",
                value="I Klubs sono vocali privati dove decidi tu chi può entrare!",
                inline=False
            )
            
            # Mostra i ruoli autorizzati
            roles_info = ""
            for role_id in self.ALLOWED_ROLE_IDS:
                role = channel.guild.get_role(role_id)
                if role:
                    roles_info += f"• {role.mention}\n"
                else:
                    roles_info += f"• <@&{role_id}> (ruolo non trovato)\n"
            
            embed.add_field(
                name="Ruoli autorizzati a creare Klubs:",
                value=roles_info if roles_info else "Nessun ruolo configurato",
                inline=False
            )
            
            embed.add_field(
                name="Comandi disponibili (prefisso >):",
                value=(
                    "`>klub create [nome]` - Crea un nuovo klub\n"
                    "`>klub edit [nome]` - Modifica il nome\n"
                    "`>klub lock` - Blocca l'accesso (solo trusted)\n"
                    "`>klub unlock` - Sblocca l'accesso\n"
                    "`>klub trust [@utente]` - Aggiungi utente trusted\n"
                    "`>klub delete` - Elimina il klub\n"
                    "`>klub_setup` - Configura il canale (solo admin)"
                ),
                inline=False
            )
            
            # Crea i pulsanti
            view = discord.ui.View(timeout=None)
            
            # Pulsante per refresh
            refresh_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="🔄 Aggiorna",
                custom_id="refresh_klubs"
            )
            
            async def refresh_callback(interaction):
                await interaction.response.defer()
                await self.send_klubs_message(channel)
                await interaction.followup.send("✅ Messaggio aggiornato!", ephemeral=True)
            
            refresh_button.callback = refresh_callback
            view.add_item(refresh_button)
            
            message = await channel.send(embed=embed, view=view)
            print(f"📨 Messaggio inviato con ID: {message.id}")
            
        except Exception as e:
            print(f"❌ Errore invio messaggio: {e}")
            import traceback
            traceback.print_exc()

    # ... (il resto dei comandi rimane uguale) ...

async def setup(bot):
    await bot.add_cog(Klubs(bot))
