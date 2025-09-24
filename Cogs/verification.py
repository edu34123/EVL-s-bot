import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione - AGGIUNTO CANALE REGOLAMENTO ITALIANO SEPARATO
        self.RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regole generale
        self.ITALIAN_RULES_CHANNEL_ID = int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1392062840097210478'))  # NUOVO: Canale regolamento italiano
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
        await asyncio.sleep(3)
        await self.setup_verification()

    async def setup_verification(self):
        """Configura i messaggi di verifica"""
        if self.verification_sent:
            return
            
        # Canale regolamento ITALIANO (nuovo canale separato)
        if self.ITALIAN_RULES_CHANNEL_ID != 0:
            await self.send_italian_rules_message()
        
        # Canale regolamento GENERALE (inglese/misto)
        if self.RULES_CHANNEL_ID != 0:
            await self.send_rules_message()
        
        # Canale verifica
        if self.VERIFY_CHANNEL_ID != 0:
            await self.send_verification_message()
        
        self.verification_sent = True

    async def send_italian_rules_message(self):
        """Invia il regolamento ITALIANO nel canale dedicato"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
            if channel:
                try:
                    # 🔥 ELIMINA TUTTI I MESSAGGI VECCHI DEL BOT NEL CANALE ITALIANO
                    async for message in channel.history(limit=20):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # EMBED REGOLAMENTO ITALIANO COMPLETO
                    embed_ita = discord.Embed(
                        title="📜 REGOLAMENTO SERVER - ITALIANO",
                        color=0x00ff00,
                        description="**Benvenuto nel server italiano!** 🇮🇹\n\nPer favore leggi attentamente il regolamento prima di partecipare."
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
                    
                    embed_ita.set_footer(text="Regolamento Sezione Italiana • Aggiornato il")
                    embed_ita.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed_ita)
                    print(f"✅ Regolamento italiano inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento italiano: {e}")

    async def send_rules_message(self):
        """Invia il messaggio del regolamento GENERALE (inglese/misto)"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulisci vecchi messaggi del bot
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # SOLO REGOLAMENTO INGLESE nel canale generale
                    embed_eng = discord.Embed(
                        title="📜 SERVER RULES - ENGLISH",
                        color=0x0099ff,
                        description="Welcome to the server! Please read the rules carefully."
                    )
                    
                    rules_eng = """
**1. Don't be toxic to other members!**
**2. No NSFW allowed!**
**3. No gore content!**
**4. No slurs or offensive language!**
**5. No spam!**
**6. Pings:**
   - Don't ping the admins!
   - Only people with special roles can be pinged
**6.1. No ghost ping**
**7. Don't share personal info!**
   - Just in <#1392062848414257204> 
**8. No offensive profile picture or names!**
**9. No impersonation!**
**10. No users under 13 years allowed!**
**11. Language:**
   - Only English and Italian please!
**12. Respect Discord's TOS!**
**13. Respect staff and their decisions!**
**14. No unauthorized advertising!**
**15. Use appropriate channels for each content!**

By accepting these rules, you confirm you have read and accepted them.
"""
                    
                    embed_eng.add_field(
                        name="Server Rules",
                        value=rules_eng,
                        inline=False
                    )
                    
                    # Aggiungi riferimento al regolamento italiano
                    if self.ITALIAN_RULES_CHANNEL_ID != 0:
                        italian_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                        if italian_channel:
                            embed_eng.add_field(
                                name="🇮🇹 Regolamento Italiano",
                                value=f"Per il regolamento completo in italiano, visita {italian_channel.mention}",
                                inline=False
                            )
                    
                    embed_eng.set_footer(text="Last update")
                    embed_eng.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed_eng)
                    print(f"✅ Regolamento generale inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento generale: {e}")

    async def send_verification_message(self):
        """Invia il messaggio di verifica"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.VERIFY_CHANNEL_ID)
            if channel:
                try:
                    # Pulisci vecchi messaggi del bot
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # Embed verifica italiano
                    embed_ita = discord.Embed(
                        title="✅ VERIFICA ACCOUNT - ITALIANO",
                        description="**Benvenuto nel server!**\n\nPer accedere a tutte le funzionalità del server, devi completare la verifica.",
                        color=0x00ff00
                    )
                    
                    # Aggiorna i riferimenti ai canali regolamento
                    rules_channel_mention = "il canale regolamento"
                    if self.ITALIAN_RULES_CHANNEL_ID != 0:
                        italian_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                        if italian_channel:
                            rules_channel_mention = italian_channel.mention
                    
                    embed_ita.add_field(
                        name="📜 Step 1: Leggi il Regolamento",
                        value=f"Assicurati di aver letto e compreso il regolamento del server in {rules_channel_mention}.",
                        inline=False
                    )
                    
                    embed_ita.add_field(
                        name="🌍 Step 2: Seleziona la tua Lingua",
                        value="Scegli se vuoi accedere alla sezione Italiana o Inglese del server.",
                        inline=False
                    )
                    
                    embed_ita.add_field(
                        name="✅ Step 3: Completa la Verifica",
                        value="Clicca il pulsante qui sotto per accettare il regolamento e selezionare la tua lingua.",
                        inline=False
                    )
                    
                    embed_ita.set_footer(text="Verifica richiesta per l'accesso al server")
                    
                    # Embed verifica inglese
                    embed_eng = discord.Embed(
                        title="✅ ACCOUNT VERIFICATION - ENGLISH",
                        description="**Welcome to the server!**\n\nTo access all server features, you need to complete verification.",
                        color=0x0099ff
                    )
                    
                    embed_eng.add_field(
                        name="📜 Step 1: Read the Rules",
                        value="Make sure you have read and understood the server rules.",
                        inline=False
                    )
                    
                    embed_eng.add_field(
                        name="🌍 Step 2: Select Your Language",
                        value="Choose whether you want to access the Italian or English section of the server.",
                        inline=False
                    )
                    
                    embed_eng.add_field(
                        name="✅ Step 3: Complete Verification",
                        value="Click the button below to accept the rules and select your language.",
                        inline=False
                    )
                    
                    embed_eng.set_footer(text="Verification required for server access")
                    
                    # Crea i pulsanti
                    view = VerifyView(self)
                    
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

    # ===============================
    # COMANDI SLASH (/)
    # ===============================

    @app_commands.command(name="verify", description="Completa la verifica del server")
    @app_commands.describe(language="Seleziona la tua lingua preferita")
    @app_commands.choices(language=[
        app_commands.Choice(name="🇮🇹 Italiano", value="ita"),
        app_commands.Choice(name="🇬🇧 English", value="eng")
    ])
    async def verify_command(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        """Comando slash per la verifica"""
        await self.complete_verification_slash(interaction, language.value)

    async def complete_verification_slash(self, interaction: discord.Interaction, language: str):
        """Completa la verifica tramite comando slash"""
        member = interaction.user
        guild = interaction.guild
        
        # Verifica che l'utente non sia già verificato
        verified_role = guild.get_role(self.VERIFIED_ROLE_ID)
        if verified_role and verified_role in member.roles:
            await interaction.response.send_message(
                "❌ Sei già verificato!\nYou are already verified!",
                ephemeral=True
            )
            return
        
        try:
            # Ruoli da gestire
            unverified_role = guild.get_role(self.UNVERIFIED_ROLE_ID)
            verified_role = guild.get_role(self.VERIFIED_ROLE_ID)
            fan_role = guild.get_role(self.FAN_ROLE_ID)
            ita_role = guild.get_role(self.ITA_ROLE_ID) if self.ITA_ROLE_ID != 0 else None
            eng_role = guild.get_role(self.ENG_ROLE_ID) if self.ENG_ROLE_ID != 0 else None
            
            # Rimuovi ruolo unverified
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
            
            # Aggiungi ruolo verified
            if verified_role and verified_role not in member.roles:
                await member.add_roles(verified_role)
            
            # Aggiungi ruolo fan
            if fan_role and fan_role not in member.roles:
                await member.add_roles(fan_role)
            
            # Gestisci ruoli lingua
            roles_to_add = []
            roles_to_remove = []
            
            if language == "ita" and ita_role:
                roles_to_add.append(ita_role)
                if eng_role and eng_role in member.roles:
                    roles_to_remove.append(eng_role)
            elif language == "eng" and eng_role:
                roles_to_add.append(eng_role)
                if ita_role and ita_role in member.roles:
                    roles_to_remove.append(ita_role)
            
            # Applica i cambiamenti
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            if roles_to_add:
                await member.add_roles(*roles_to_add)
            
            # Messaggio di conferma
            if language == "ita":
                message = (
                    "✅ **Verifica completata!**\n\n"
                    "🇮🇹 **Sezione Italiana** attivata\n"
                    "🎯 Ruolo **Fan** assegnato\n"
                    "🔓 Accesso al server sbloccato\n\n"
                    f"📖 Leggi il regolamento completo in <#{self.ITALIAN_RULES_CHANNEL_ID}>\n"
                    "Benvenuto nella community! 🎉"
                )
            else:
                message = (
                    "✅ **Verification completed!**\n\n"
                    "🇬🇧 **English Section** activated\n"
                    "🎯 **Fan** role assigned\n"
                    "🔓 Server access unlocked\n\n"
                    "Welcome to the community! 🎉"
                )
            
            embed = discord.Embed(
                description=message,
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Messaggio nel canale generale (opzionale)
            try:
                general_channel = guild.system_channel
                if general_channel:
                    if language == "ita":
                        welcome_msg = f"🎉 **Benvenuto** {member.mention} nella **sezione italiana**! Dai il benvenuto! 👋"
                    else:
                        welcome_msg = f"🎉 **Welcome** {member.mention} to the **english section**! Say hello! 👋"
                    
                    await general_channel.send(welcome_msg, delete_after=10)
            except:
                pass
            
            print(f"✅ Utente verificato via slash: {member.display_name} ({language})")
            
        except Exception as e:
            print(f"❌ Errore verifica slash: {e}")
            error_msg = "❌ Errore durante la verifica. Contatta lo staff.\nError during verification. Contact staff."
            await interaction.response.send_message(error_msg, ephemeral=True)

    # ... (mantieni il resto del codice invariato per i comandi slash)

class VerifyView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="🎯 Inizia Verifica / Start Verification", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestisce il pulsante di verifica"""
        # Verifica che l'utente non sia già verificato
        member = interaction.user
        verified_role = interaction.guild.get_role(self.cog.VERIFIED_ROLE_ID)
        
        if verified_role and verified_role in member.roles:
            await interaction.response.send_message(
                "❌ Sei già verificato!\nYou are already verified!",
                ephemeral=True
            )
            return
        
        # Crea l'embed di selezione lingua
        embed = discord.Embed(
            title="🌍 Seleziona Lingua / Select Language",
            description=(
                "**Sei italiano o preferisci l'italiano?** → Clicca **Italiano**\n"
                "**Are you English or prefer English?** → Click **English**\n\n"
                "Questa scelta determinerà quale sezione del server vedrai.\n"
                "This choice will determine which server section you'll see."
            ),
            color=0x0099ff
        )
        
        # Aggiungi riferimento al canale regolamento italiano
        if self.cog.ITALIAN_RULES_CHANNEL_ID != 0:
            italian_channel = interaction.guild.get_channel(self.cog.ITALIAN_RULES_CHANNEL_ID)
            if italian_channel:
                embed.add_field(
                    name="🇮🇹 Regolamento Italiano",
                    value=f"Il regolamento completo in italiano è disponibile in {italian_channel.mention}",
                    inline=False
                )
        
        embed.add_field(
            name="🇮🇹 Sezione Italiana",
            value="• Canali in italiano\n• Community italiana\n• Eventi in italiano",
            inline=True
        )
        
        embed.add_field(
            name="🇬🇧 English Section", 
            value="• English channels\n• International community\n• English events",
            inline=True
        )
        
        # Crea i pulsanti per la selezione lingua
        view = LanguageView(self.cog)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class LanguageView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="🇮🇹 Italiano", style=discord.ButtonStyle.primary, custom_id="select_ita")
    async def ita_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.complete_verification(interaction, "ita")
    
    @discord.ui.button(label="🇬🇧 English", style=discord.ButtonStyle.primary, custom_id="select_eng")
    async def eng_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.complete_verification(interaction, "eng")

    async def complete_verification(self, interaction, language):
        """Completa la verifica assegnando i ruoli"""
        member = interaction.user
        guild = interaction.guild
        
        try:
            # Ruoli da gestire
            unverified_role = guild.get_role(self.cog.UNVERIFIED_ROLE_ID)
            verified_role = guild.get_role(self.cog.VERIFIED_ROLE_ID)
            fan_role = guild.get_role(self.cog.FAN_ROLE_ID)
            ita_role = guild.get_role(self.cog.ITA_ROLE_ID) if self.cog.ITA_ROLE_ID != 0 else None
            eng_role = guild.get_role(self.cog.ENG_ROLE_ID) if self.cog.ENG_ROLE_ID != 0 else None
            
            # Rimuovi ruolo unverified
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
            
            # Aggiungi ruolo verified
            if verified_role and verified_role not in member.roles:
                await member.add_roles(verified_role)
            
            # Aggiungi ruolo fan
            if fan_role and fan_role not in member.roles:
                await member.add_roles(fan_role)
            
            # Gestisci ruoli lingua
            roles_to_add = []
            roles_to_remove = []
            
            if language == "ita" and ita_role:
                roles_to_add.append(ita_role)
                if eng_role and eng_role in member.roles:
                    roles_to_remove.append(eng_role)
            elif language == "eng" and eng_role:
                roles_to_add.append(eng_role)
                if ita_role and ita_role in member.roles:
                    roles_to_remove.append(ita_role)
            
            # Applica i cambiamenti
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            if roles_to_add:
                await member.add_roles(*roles_to_add)
            
            # Messaggio di conferma
            if language == "ita":
                message = (
                    "✅ **Verifica completata!** Sezione Italiana attivata.\n\n"
                    f"📖 Leggi il regolamento completo in <#{self.cog.ITALIAN_RULES_CHANNEL_ID}>\n"
                    "Benvenuto! 🎉"
                )
            else:
                message = "✅ **Verification completed!** English Section activated. Welcome! 🎉"
            
            embed = discord.Embed(description=message, color=0x00ff00)
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            print(f"❌ Errore verifica: {e}")
            error_msg = "❌ Errore durante la verifica. Contatta lo staff."
            await interaction.response.edit_message(content=error_msg, embed=None, view=None)

async def setup(bot):
    await bot.add_cog(Verification(bot))
