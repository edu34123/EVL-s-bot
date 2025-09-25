import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione - VERIFICA CHE GLI ID SIANO DIVERSI
        self.RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regole INGLESE
        self.ITALIAN_RULES_CHANNEL_ID = int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regolamento ITALIANO
        self.VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID', '1392062838197059644'))
        
        # Ruoli
        self.UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID', '1392111556954685450'))
        self.VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID', '1392128530438951084'))
        self.ITA_ROLE_ID = int(os.getenv('ITA_ROLE_ID', '1402668379533348944'))
        self.ENG_ROLE_ID = int(os.getenv('ENG_ROLE_ID', '1402668928890568785'))
        self.FAN_ROLE_ID = int(os.getenv('FAN_ROLE_ID', '1392128530438951084'))
        
        self.verification_sent = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Inizializza il sistema di verifica"""
        print("✅ Sistema di Verifica caricato!")
        
        # VERIFICA SE I CANALI SONO DIVERSI
        if self.RULES_CHANNEL_ID == self.ITALIAN_RULES_CHANNEL_ID:
            print("⚠️ ATTENZIONE: RULES_CHANNEL_ID e ITALIAN_RULES_CHANNEL_ID sono uguali!")
            print("📝 Il regolamento italiano verrà inviato nello stesso canale di quello inglese")
        
        await asyncio.sleep(3)
        await self.setup_verification()

    async def setup_verification(self):
        """Configura i messaggi di verifica"""
        if self.verification_sent:
            return
            
        print("🔄 Invio regolamenti...")
        
        # PRIMA invia il regolamento ITALIANO
        if self.ITALIAN_RULES_CHANNEL_ID != 0:
            await self.send_italian_rules_message()
            await asyncio.sleep(2)  # Attendi tra un invio e l'altro
        
        # POI invia il regolamento INGLESE
        if self.RULES_CHANNEL_ID != 0:
            await self.send_rules_message()
            await asyncio.sleep(2)
        
        # INFINE invia il messaggio di verifica
        if self.VERIFY_CHANNEL_ID != 0:
            await self.send_verification_message()
        
        self.verification_sent = True
        print("✅ Tutti i regolamenti inviati correttamente!")

    async def send_italian_rules_message(self):
        """Invia il regolamento ITALIANO nel canale dedicato"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
            if channel:
                try:
                    # 🔥 ELIMINA TUTTI I MESSAGGI VECCHI DEL BOT NEL CANALE ITALIANO
                    print(f"🔄 Pulizia canale italiano: #{channel.name}")
                    async for message in channel.history(limit=20):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                                await asyncio.sleep(0.5)
                            except:
                                pass
                    
                    await asyncio.sleep(2)
                    
                    # EMBED REGOLAMENTO ITALIANO COMPLETO
                    embed_ita = discord.Embed(
                        title="📜 REGOLAMENTO SERVER - ITALIANO 🇮🇹",
                        color=0x00ff00,
                        description="**Benvenuto nel server italiano!**\n\nPer favore leggi attentamente il regolamento prima di partecipare."
                    )
                    
                    rules_ita = """
**📋 REGOLE GENERALI DEL SERVER**

**1. RISPETTO E EDUCAZIONE**
• Non essere tossico con gli altri membri
• Nessun insulto o linguaggio offensivo
• Rispetta lo staff e le loro decisioni

**2. CONTENUTI VIETATI**
• Nessun contenuto NSFW o inappropriate
• Nessun contenuto gore o violento
• No spam o flood nei messaggi

**3. SICUREZZA E PRIVACY**
• Non condividere informazioni personali (tranne in <#1392062848414257204>)
• Nessuna impersonazione di altri utenti
• Rispetta i Termini di Servizio di Discord

**4. COMUNICAZIONE**
• Usa i canali appropriati per ogni contenuto
• No ghost ping o mention inappropriate
• Non pingare gli admin senza motivo

**5. ALTRE REGOLE IMPORTANTI**
• Nessun utente sotto i 13 anni permesso
• Nessuna immagine profilo o nome offensivo
• No pubblicità non autorizzata

**🎯 REGOLE SEZIONE ITALIANA**
• Usa l'italiano come lingua principale
• Rispetta la cultura italiana
• Partecipa agli eventi della community italiana

**⚠️ SANZIONI**
Il mancato rispetto di queste regole comporterà:
• Avvertimento → Mute temporaneo → Ban

Accettando queste regole, confermi di averle lette e accettate.
"""
                    
                    embed_ita.add_field(
                        name="Regolamento Completo",
                        value=rules_ita,
                        inline=False
                    )
                    
                    embed_ita.add_field(
                        name="📞 Contatti Staff",
                        value="Per problemi o segnalazioni, contatta lo staff italiano",
                        inline=False
                    )
                    
                    embed_ita.set_footer(text="Regolamento Sezione Italiana")
                    embed_ita.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed_ita)
                    print(f"✅ Regolamento ITALIANO inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento italiano: {e}")

    async def send_rules_message(self):
        """Invia il messaggio del regolamento INGLESE nel canale dedicato"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulisci vecchi messaggi del bot SOLO se è un canale diverso
                    if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        print(f"🔄 Pulizia canale inglese: #{channel.name}")
                        async for message in channel.history(limit=10):
                            if message.author == self.bot.user:
                                try:
                                    await message.delete()
                                    await asyncio.sleep(0.5)
                                except:
                                    pass
                    
                    await asyncio.sleep(2)
                    
                    # EMBED REGOLAMENTO INGLESE
                    embed_eng = discord.Embed(
                        title="📜 SERVER RULES - ENGLISH 🇬🇧",
                        color=0x0099ff,
                        description="**Welcome to the server!**\n\nPlease read the rules carefully before participating."
                    )
                    
                    rules_eng = """
**📋 SERVER RULES**

**1. RESPECT AND EDUCATION**
• Don't be toxic to other members
• No insults or offensive language
• Respect staff and their decisions

**2. PROHIBITED CONTENT**
• No NSFW or inappropriate content
• No gore or violent content
• No spam or message flooding

**3. SAFETY AND PRIVACY**
• Don't share personal information (except in <#1392062848414257204>)
• No impersonation of other users
• Respect Discord's Terms of Service

**4. COMMUNICATION**
• Use appropriate channels for each content
• No ghost ping or inappropriate mentions
• Don't ping admins without reason

**5. OTHER IMPORTANT RULES**
• No users under 13 years allowed
• No offensive profile pictures or names
• No unauthorized advertising

**🎯 ENGLISH SECTION RULES**
• Use English as main language
• Respect international community
• Participate in English events

**⚠️ SANCTIONS**
Failure to comply with these rules will result in:
• Warning → Temporary mute → Ban

By accepting these rules, you confirm you have read and accepted them.
"""
                    
                    embed_eng.add_field(
                        name="Complete Rules",
                        value=rules_eng,
                        inline=False
                    )
                    
                    # Se i canali sono diversi, aggiungi riferimento al regolamento italiano
                    if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        italian_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                        if italian_channel:
                            embed_eng.add_field(
                                name="🇮🇹 Italian Rules",
                                value=f"For complete rules in Italian, visit {italian_channel.mention}",
                                inline=False
                            )
                    
                    embed_eng.set_footer(text="Server Rules - English Version")
                    embed_eng.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed_eng)
                    print(f"✅ Regolamento INGLESE inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento inglese: {e}")

    async def send_verification_message(self):
        """Invia il messaggio di verifica"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.VERIFY_CHANNEL_ID)
            if channel:
                try:
                    # Pulisci vecchi messaggi del bot
                    print(f"🔄 Pulizia canale verifica: #{channel.name}")
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                                await asyncio.sleep(0.5)
                            except:
                                pass
                    
                    await asyncio.sleep(2)
                    
                    # Embed verifica italiano
                    embed_ita = discord.Embed(
                        title="✅ VERIFICA ACCOUNT - ITALIANO 🇮🇹",
                        description="**Benvenuto nel server!**\n\nPer accedere a tutte le funzionalità del server, devi completare la verifica.",
                        color=0x00ff00
                    )
                    
                    # Riferimenti ai canali regolamento
                    italian_rules_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                    english_rules_channel = guild.get_channel(self.RULES_CHANNEL_ID)
                    
                    rules_references = ""
                    if italian_rules_channel:
                        rules_references += f"• 🇮🇹 Regolamento italiano: {italian_rules_channel.mention}\n"
                    if english_rules_channel and self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        rules_references += f"• 🇬🇧 English rules: {english_rules_channel.mention}\n"
                    
                    embed_ita.add_field(
                        name="📜 Leggi il Regolamento",
                        value=f"Prima di verificarti, assicurati di aver letto:\n{rules_references}",
                        inline=False
                    )
                    
                    embed_ita.add_field(
                        name="🌍 Seleziona Lingua",
                        value="Scegli se vuoi accedere alla sezione Italiana o Inglese del server.",
                        inline=False
                    )
                    
                    embed_ita.add_field(
                        name="✅ Completa la Verifica",
                        value="Clicca il pulsante qui sotto per accettare il regolamento e selezionare la tua lingua.",
                        inline=False
                    )
                    
                    embed_ita.set_footer(text="Verifica richiesta per l'accesso al server")
                    
                    # Embed verifica inglese
                    embed_eng = discord.Embed(
                        title="✅ ACCOUNT VERIFICATION - ENGLISH 🇬🇧",
                        description="**Welcome to the server!**\n\nTo access all server features, you need to complete verification.",
                        color=0x0099ff
                    )
                    
                    embed_eng.add_field(
                        name="📜 Read the Rules",
                        value=f"Before verifying, make sure you've read:\n{rules_references}",
                        inline=False
                    )
                    
                    embed_eng.add_field(
                        name="🌍 Select Language", 
                        value="Choose whether you want to access the Italian or English section of the server.",
                        inline=False
                    )
                    
                    embed_eng.add_field(
                        name="✅ Complete Verification",
                        value="Click the button below to accept the rules and select your language.",
                        inline=False
                    )
                    
                    embed_eng.set_footer(text="Verification required for server access")
                    
                    # Crea i pulsanti
                    view = VerifyView(self)
                    
                    # Invia i messaggi
                    await channel.send(embed=embed_ita)
                    await asyncio.sleep(1)
                    await channel.send(embed=embed_eng)
                    await asyncio.sleep(1)
                    await channel.send(
                        "**Clicca il pulsante qui sotto per iniziare la verifica:**\n"
                        "**Click the button below to start verification:**",
                        view=view
                    )
                    
                    print(f"✅ Messaggio verifica inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio verifica: {e}")

    # ... (mantieni il resto del codice invariato per i comandi slash e i pulsanti)

class VerifyView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="🎯 Inizia Verifica / Start Verification", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestisce il pulsante di verifica"""
        # ... (codice invariato)

class LanguageView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="🇮🇹 Italiano", style=discord.ButtonStyle.primary, custom_id="select_ita")
    async def ita_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.complete_verification(interaction, "ita")
    
    @discord.ui.button(label="🇬🇧 English", style=discord.ButtonStyle.primary, custom_id="select_eng")
    async def eng_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.complete_verification(interaction, "eng")

    async def complete_verification(self, interaction, language):
        """Completa la verifica assegnando i ruoli"""
        # ... (codice invariato)

async def setup(bot):
    await bot.add_cog(Verification(bot))
