import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class VerificationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione - IMPORTANTE: usa ID DIVERSI per i due canali!
        self.RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regole inglese
        self.ITALIAN_RULES_CHANNEL_ID = int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1392062838197059644'))  # Canale regole italiano (DIVERSO!)
        self.VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID', '1392062838197059644'))  # Canale verifica
        
        # Ruoli
        self.UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID', '1392111556954685450'))
        self.VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID', '1392128530438951084'))
        self.ITA_ROLE_ID = int(os.getenv('ITA_ROLE_ID', '1402668379533348944'))
        self.ENG_ROLE_ID = int(os.getenv('ENG_ROLE_ID', '1402668928890568785'))
        self.FAN_ROLE_ID = int(os.getenv('FAN_ROLE_ID', '1392128530438951084'))
        
        self.verification_setup_done = False

    async def complete_verification(self, interaction: discord.Interaction, language: str):
        """Completa la verifica e assegna i ruoli"""
        try:
            guild = interaction.guild
            member = interaction.user
            
            # Rimuovi ruolo non verificato e aggiungi ruolo verificato
            unverified_role = guild.get_role(self.UNVERIFIED_ROLE_ID)
            verified_role = guild.get_role(self.VERIFIED_ROLE_ID)
            
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
            
            if verified_role and verified_role not in member.roles:
                await member.add_roles(verified_role)
            
            # Assegna ruolo lingua
            if language == "ita":
                ita_role = guild.get_role(self.ITA_ROLE_ID)
                eng_role = guild.get_role(self.ENG_ROLE_ID)
                
                if ita_role and ita_role not in member.roles:
                    await member.add_roles(ita_role)
                if eng_role and eng_role in member.roles:
                    await member.remove_roles(eng_role)
                
                message = "✅ Verifica completata! Sezione Italiana attivata. Benvenuto! 🎉"
            else:
                eng_role = guild.get_role(self.ENG_ROLE_ID)
                ita_role = guild.get_role(self.ITA_ROLE_ID)
                
                if eng_role and eng_role not in member.roles:
                    await member.add_roles(eng_role)
                if ita_role and ita_role in member.roles:
                    await member.remove_roles(ita_role)
                
                message = "✅ Verification completed! English Section activated. Welcome! 🎉"
            
            embed = discord.Embed(description=message, color=0x00ff00)
            await interaction.response.edit_message(embed=embed, view=None)
            
            print(f"✅ Verifica completata per {member.display_name} ({language})")
            
        except Exception as e:
            error_embed = discord.Embed(
                description="❌ Errore durante la verifica. Contatta lo staff.",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=error_embed, view=None)
            print(f"❌ Errore verifica per {interaction.user.display_name}: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Avvia automaticamente il setup quando il bot è pronto"""
        print("✅ Sistema di Verifica caricato!")
        
        # Aspetta che il bot sia completamente pronto
        await asyncio.sleep(5)
        
        # Esegui il setup solo se non è già stato fatto
        if not self.verification_setup_done:
            await self.setup_verification_system()

    async def setup_verification_system(self):
        """Setup completo del sistema di verifica"""
        print("🔄 AVVIO SETUP AUTOMATICO DEL SISTEMA DI VERIFICA...")
        
        try:
            # 1. PRIMA invia il REGOLAMENTO ITALIANO (in canale italiano)
            if self.ITALIAN_RULES_CHANNEL_ID != 0:
                print("📜 Invio regolamento italiano...")
                await self.send_italian_rules()
                await asyncio.sleep(3)
            else:
                print("❌ Canale regolamento italiano non configurato")

            # 2. POI invia il REGOLAMENTO INGLESE (in canale inglese)
            if self.RULES_CHANNEL_ID != 0 and self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                print("📜 Invio regolamento inglese...")
                await self.send_english_rules()
                await asyncio.sleep(3)
            else:
                print("❌ Canale regolamento inglese non configurato o uguale a italiano")

            # 3. INFINE invia il MESSAGGIO di VERIFICA
            if self.VERIFY_CHANNEL_ID != 0:
                print("✅ Invio messaggio di verifica...")
                await self.send_verification_message()
                await asyncio.sleep(2)
            else:
                print("❌ Canale verifica non configurato")

            self.verification_setup_done = True
            print("🎉 SETUP COMPLETATO! Regolamento e verifica inviati correttamente!")

        except Exception as e:
            print(f"❌ ERRORE durante il setup: {e}")

    async def send_italian_rules(self):
        """Invia il regolamento italiano nel canale italiano"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia messaggi vecchi del bot SOLO in questo canale
                    print(f"🧹 Pulizia canale italiano: #{channel.name} (ID: {channel.id})")
                    async for message in channel.history(limit=20):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO ITALIANO AGGIORNATO
                    embed = discord.Embed(
                        title="📜 REGOLAMENTO DEL SERVER - ITALIANO 🇮🇹",
                        color=0x00ff00,
                        description="**Benvenuti sul server! Si prega di leggere attentamente le regole prima di partecipare.**"
                    )
                    
                    rules_text = """
**1. RISPETTO E COMPORTAMENTO**

• Non essere nocivo per gli altri membri!
• Niente insulti, discriminazioni o incitamenti all'odio
• Rispetta lo staff e le sue decisioni

**2. CONTENUTI VIETATI**

• Vietato ai minori di 18 anni!
• Nessun contenuto sanguinolento!
• Niente insulti o linguaggio offensivo!
• Niente spam o inondazioni di messaggi!

**3. REGOLE PER PING E MENTION**

• Non inviare ping agli amministratori!
• Solo le persone con ruoli speciali possono inviare ping allo staff
• Niente ping fantasma

**4. SICUREZZA E PRIVACY**

• Non condividere informazioni personali!
• Condividi informazioni personali solo nel canale di presentazione
• Niente immagini o nomi offensivi del profilo!
• Nessuna imitazione di altri utenti!

**5. REQUISITI DI ETÀ E LINGUA**

• Vietato l'accesso agli utenti di età inferiore ai 13 anni!
• Solo inglese e italiano, per favore!
• Rispetta i Termini di servizio di Discord!

**⛔ SANZIONI**

Il mancato rispetto di queste regole comporterà:
• 🟡 Avvertimento
• 🔴 Disattivazione temporanea
• 🔴 Ban permanente per recidive

**Accettando queste regole, confermi di averle lette e accettate.**
"""
                    
                    embed.add_field(name="Regole complete del server", value=rules_text, inline=False)
                    embed.set_footer(text="Regolamento Server Italiano")
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento italiano inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore regolamento italiano in #{channel.name}: {e}")

    async def send_english_rules(self):
        """Invia il regolamento inglese nel canale inglese"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia solo se canale diverso da italiano
                    if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        print(f"🧹 Pulizia canale inglese: #{channel.name} (ID: {channel.id})")
                        async for message in channel.history(limit=20):
                            if message.author == self.bot.user:
                                await message.delete()
                                await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO INGLESE
                    embed = discord.Embed(
                        title="📜 SERVER RULES - ENGLISH 🇬🇧",
                        color=0x0099ff,
                        description="**Welcome to the server! Please read the rules carefully before participating.**"
                    )
                    
                    rules_text = """
**1. RESPECT AND BEHAVIOR**
• Don't be toxic to other members!
• No insults, discrimination or hate speech
• Respect staff and their decisions

**2. PROHIBITED CONTENT**
• No NSFW allowed!
• No gore content!
• No slurs or offensive language!
• No spam or message flooding!

**3. PING AND MENTION RULES**
• Don't ping the admins!
• Only people with special roles can be pinged
• No ghost ping

**4. SAFETY AND PRIVACY**
• Don't share personal info!
• Only share personal information in introductions channel
• No offensive profile pictures or names!
• No impersonation of other users!

**5. AGE AND LANGUAGE REQUIREMENTS**
• No users under 13 years allowed!
• Only English and Italian languages please!
• Respect Discord's Terms of Service!

**⛔ SANCTIONS**
Failure to comply with these rules will result in:
• 🟡 Warning
• 🔴 Temporary mute
• 🔴 Permanent ban for repeat offenses

By accepting these rules, you confirm you have read and accepted them.
"""
                    
                    embed.add_field(name="Complete Server Rules", value=rules_text, inline=False)
                    embed.set_footer(text="Server Rules - English Version")
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento inglese inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore regolamento inglese in #{channel.name}: {e}")

    async def send_verification_message(self):
        """Invia il messaggio di verifica"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.VERIFY_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia messaggi vecchi
                    print(f"🧹 Pulizia canale verifica: #{channel.name}")
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # MESSAGGIO DI VERIFICA COMPLETO
                    embed = discord.Embed(
                        title="✅ VERIFICA ACCOUNT / ACCOUNT VERIFICATION",
                        color=0xffff00
                    )
                    
                    embed.description = (
                        "**Benvenuto nel server!** 🇮🇹\n"
                        "**Welcome to the server!** 🇬🇧\n\n"
                        
                        "Per accedere a tutte le funzionalità, completa la verifica.\n"
                        "To access all features, complete the verification."
                    )
                    
                    # Riferimenti ai canali regolamento
                    rules_refs = ""
                    italian_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                    english_channel = guild.get_channel(self.RULES_CHANNEL_ID)
                    
                    if italian_channel:
                        rules_refs += f"• 🇮🇹 **Regolamento Italiano:** {italian_channel.mention}\n"
                    if english_channel and self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        rules_refs += f"• 🇬🇧 **English Rules:** {english_channel.mention}\n"
                    
                    embed.add_field(
                        name="📜 LEGGI IL REGOLAMENTO / READ THE RULES",
                        value=f"Prima di verificarti, leggi le regole:\n{rules_refs}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🌍 SELEZIONA LINGUA / SELECT LANGUAGE",
                        value=(
                            "**🇮🇹 Italiano** - Se sei italiano o preferisci l'italiano\n"
                            "**🇬🇧 English** - Se preferisci l'inglese\n\n"
                            "La scelta determina la sezione del server che vedrai."
                        ),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="✅ COMPLETA LA VERIFICA / COMPLETE VERIFICATION",
                        value="Clicca il pulsante sotto per iniziare la verifica.",
                        inline=False
                    )
                    
                    embed.set_footer(text="Verifica richiesta per l'accesso completo al server")
                    
                    # Crea il pulsante di verifica
                    view = discord.ui.View(timeout=None)
                    view.add_item(VerifyButton())
                    
                    # Invia il messaggio
                    await channel.send(
                        content=(
                            "**👇 CLICCA IL PULSANTE PER VERIFICARTI 👇**\n"
                            "**👇 CLICK THE BUTTON TO VERIFY 👇**"
                        ),
                        embed=embed,
                        view=view
                    )
                    
                    print(f"✅ Messaggio di verifica inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio verifica: {e}")

    # COMANDO PER FORZARE IL RE-INVIO
    @app_commands.command(name="setup_verify", description="Re-invia regolamento e verifica (Admin)")
    @app_commands.default_permissions(administrator=True)
    async def setup_verify(self, interaction: discord.Interaction):
        """Comando admin per re-inviare i messaggi"""
        await interaction.response.defer(ephemeral=True)
        
        self.verification_setup_done = False
        await self.setup_verification_system()
        
        await interaction.followup.send("✅ Regolamento e verifica re-inviati!", ephemeral=True)

class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🎯 Inizia Verifica / Start Verification",
            style=discord.ButtonStyle.success,
            custom_id="verify_start_button",
            emoji="✅"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Gestisce il pulsante di verifica"""
        cog = interaction.client.get_cog('VerificationSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema di verifica non disponibile", ephemeral=True)
            return
        
        # Embed di selezione lingua
        embed = discord.Embed(
            title="🌍 Seleziona Lingua / Select Language",
            color=0x0099ff,
            description=(
                "**Sei italiano o preferisci l'italiano?** → Clicca **Italiano**\n"
                "**Are you English or prefer English?** → Click **English**\n\n"
                "La scelta determina la sezione del server che vedrai."
            )
        )
        
        # Crea i pulsanti per la selezione lingua
        view = discord.ui.View(timeout=180)
        
        ita_button = discord.ui.Button(
            label="🇮🇹 Italiano",
            style=discord.ButtonStyle.primary,
            custom_id="verify_ita"
        )
        
        eng_button = discord.ui.Button(
            label="🇬🇧 English",
            style=discord.ButtonStyle.primary,
            custom_id="verify_eng"
        )
        
        # Callbacks
        async def ita_callback(interaction):
            await cog.complete_verification(interaction, "ita")
        
        async def eng_callback(interaction):
            await cog.complete_verification(interaction, "eng")
        
        ita_button.callback = ita_callback
        eng_button.callback = eng_callback
        
        view.add_item(ita_button)
        view.add_item(eng_button)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(VerificationSystem(bot))
