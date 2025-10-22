import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class VerificationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione
        self.RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regole inglese
        self.ITALIAN_RULES_CHANNEL_ID = int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1420636068319068160'))  # Canale regole italiano
        self.VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID', '1392062838197059644'))  # Canale verifica
        
        # Ruoli
        self.UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID', '1392111556954685450'))
        self.VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID', '1392128530438951084'))
        self.ITA_ROLE_ID = int(os.getenv('ITA_ROLE_ID', '1402668379533348944'))
        self.ENG_ROLE_ID = int(os.getenv('ENG_ROLE_ID', '1402668928890568785'))
        
        self.verification_setup_done = False
        print(f"🔧 VerificationSystem inizializzato - Canale Italiano: {self.ITALIAN_RULES_CHANNEL_ID}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Avvia automaticamente il setup quando il bot è pronto"""
        print("✅ Sistema di Verifica ON_READY attivato!")
        
        # Aspetta che il bot sia completamente pronto
        await asyncio.sleep(10)
        
        # Esegui il setup solo se non è già stato fatto
        if not self.verification_setup_done:
            print("🔄 Avvio setup verifica...")
            await self.setup_verification_system()
        else:
            print("ℹ️ Setup verifica già completato precedentemente")

    async def setup_verification_system(self):
        """Setup completo del sistema di verifica"""
        print("🔄 AVVIO SETUP AUTOMATICO DEL SISTEMA DI VERIFICA...")
        
        try:
            # 1. PRIMA invia il REGOLAMENTO ITALIANO
            print(f"📜 Tentativo invio regolamento italiano in canale: {self.ITALIAN_RULES_CHANNEL_ID}")
            if self.ITALIAN_RULES_CHANNEL_ID != 0:
                await self.send_italian_rules()
                await asyncio.sleep(3)
            else:
                print("❌ Canale regolamento italiano non configurato (ID: 0)")

            # 2. POI invia il REGOLAMENTO INGLESE
            print(f"📜 Tentativo invio regolamento inglese in canale: {self.RULES_CHANNEL_ID}")
            if self.RULES_CHANNEL_ID != 0 and self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                await self.send_english_rules()
                await asyncio.sleep(3)
            else:
                print("❌ Canale regolamento inglese non configurato o uguale a italiano")

            # 3. INFINE invia il MESSAGGIO di VERIFICA
            print(f"✅ Tentativo invio verifica in canale: {self.VERIFY_CHANNEL_ID}")
            if self.VERIFY_CHANNEL_ID != 0:
                await self.send_verification_message()
                await asyncio.sleep(2)
            else:
                print("❌ Canale verifica non configurato (ID: 0)")

            self.verification_setup_done = True
            print("🎉 SETUP COMPLETATO! Regolamento e verifica inviati correttamente!")

        except Exception as e:
            print(f"❌ ERRORE durante il setup: {e}")

    async def send_italian_rules(self):
        """Invia il regolamento italiano nel canale italiano"""
        print(f"🔍 Ricerca canale italiano ID: {self.ITALIAN_RULES_CHANNEL_ID}")
        
        for guild in self.bot.guilds:
            print(f"🔍 Controllo server: {guild.name} (ID: {guild.id})")
            channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
            
            if channel:
                print(f"✅ Canale italiano trovato: #{channel.name} (ID: {channel.id})")
                try:
                    # Pulizia messaggi vecchi del bot
                    print(f"🧹 Pulizia canale italiano: #{channel.name}")
                    deleted_count = 0
                    async for message in channel.history(limit=30):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                                deleted_count += 1
                                await asyncio.sleep(0.5)
                            except Exception as e:
                                print(f"⚠️ Errore cancellazione messaggio: {e}")
                    
                    print(f"🗑️ Cancellati {deleted_count} messaggi vecchi")
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO ITALIANO AGGIORNATO - FORMATTO CORRETTAMENTE
                    embed = discord.Embed(
                        title="📜 REGOLAMENTO DEL SERVER - ITALIANO",
                        color=0x00ff00,
                        description="**Benvenuti sul server! Si prega di leggere attentamente le regole prima di partecipare.**"
                    )
                    
                    # Testo del regolamento formattato correttamente
                    rules_sections = [
                        ("1. RISPETTO E COMPORTAMENTO", """
• Non essere nocivo per gli altri membri!
• Niente insulti, discriminazioni o incitamenti all'odio
• Rispetta lo staff e le sue decisioni"""),

                        ("2. CONTENUTI VIETATI", """
• Vietato ai minori di 18 anni!
• Nessun contenuto sanguinolento!
• Niente insulti o linguaggio offensivo!
• Niente spam o inondazioni di messaggi!"""),

                        ("3. REGOLE PER PING E MENTION", """
• Non inviare ping agli amministratori!
• Solo le persone con ruoli speciali possono inviare ping allo staff
• Niente ping fantasma"""),

                        ("4. SICUREZZA E PRIVACY", """
• Non condividere informazioni personali!
• Condividi informazioni personali solo nel canale di presentazione
• Niente immagini o nomi offensivi del profilo!
• Nessuna imitazione di altri utenti!"""),

                        ("5. REQUISITI DI ETÀ E LINGUA", """
• Vietato l'accesso agli utenti di età inferiore ai 13 anni!
• Solo inglese e italiano, per favore!
• Rispetta i Termini di servizio di Discord!"""),

                        ("⛔ SANZIONI", """
Il mancato rispetto di queste regole comporterà:
• 🟡 Avvertimento
• 🔴 Disattivazione temporanea
• 🔴 Ban permanente per recidive

**Accettando queste regole, confermi di averle lette e accettate.**""")
                    ]
                    
                    # Aggiungi ogni sezione come campo separato
                    for title, content in rules_sections:
                        embed.add_field(name=title, value=content, inline=False)
                    
                    embed.set_footer(text="Regolamento Server Italiano")
                    
                    # Prova a inviare l'embed
                    await channel.send(embed=embed)
                    print(f"✅ REGOLAMENTO ITALIANO INVIATO CON SUCCESSO in #{channel.name}!")
                    
                except discord.HTTPException as e:
                    print(f"❌ Errore HTTP durante l'invio in #{channel.name}: {e}")
                    # Fallback: prova a inviare come messaggio di testo semplice
                    await self.send_rules_as_text(channel, "italiano")
                except Exception as e:
                    print(f"❌ Errore imprevisto in #{channel.name}: {e}")
                    # Fallback: prova a inviare come messaggio di testo semplice
                    await self.send_rules_as_text(channel, "italiano")
            else:
                print(f"❌ Canale italiano NON TROVATO nel server {guild.name}! ID: {self.ITALIAN_RULES_CHANNEL_ID}")

    async def send_rules_as_text(self, channel, language):
        """Invia il regolamento come messaggio di testo semplice (fallback)"""
        try:
            if language == "italiano":
                rules_text = """
**📜 REGOLAMENTO DEL SERVER - ITALIANO 🇮🇹**

**Benvenuti sul server! Si prega di leggere attentamente le regole prima di partecipare.**

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
            else:
                rules_text = """
**📜 SERVER RULES - ENGLISH 🇬🇧**

**Welcome to the server! Please read the rules carefully before participating.**

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
            
            # Dividi il messaggio se troppo lungo
            if len(rules_text) > 2000:
                chunks = [rules_text[i:i+2000] for i in range(0, len(rules_text), 2000)]
                for chunk in chunks:
                    await channel.send(chunk)
                    await asyncio.sleep(1)
            else:
                await channel.send(rules_text)
            
            print(f"✅ Regolamento {language} inviato come testo in #{channel.name}")
            
        except Exception as e:
            print(f"❌ Errore anche con invio testo in #{channel.name}: {e}")

    async def send_english_rules(self):
        """Invia il regolamento inglese nel canale inglese"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia solo se canale diverso da italiano
                    if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        print(f"🧹 Pulizia canale inglese: #{channel.name}")
                        async for message in channel.history(limit=20):
                            if message.author == self.bot.user:
                                await message.delete()
                                await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO INGLESE - FORMATTO CORRETTAMENTE
                    embed = discord.Embed(
                        title="📜 SERVER RULES - ENGLISH",
                        color=0x0099ff,
                        description="**Welcome to the server! Please read the rules carefully before participating.**"
                    )
                    
                    rules_sections = [
                        ("1. RESPECT AND BEHAVIOR", """
• Don't be toxic to other members!
• No insults, discrimination or hate speech
• Respect staff and their decisions"""),

                        ("2. PROHIBITED CONTENT", """
• No NSFW allowed!
• No gore content!
• No slurs or offensive language!
• No spam or message flooding!"""),

                        ("3. PING AND MENTION RULES", """
• Don't ping the admins!
• Only people with special roles can be pinged
• No ghost ping"""),

                        ("4. SAFETY AND PRIVACY", """
• Don't share personal info!
• Only share personal information in introductions channel
• No offensive profile pictures or names!
• No impersonation of other users!"""),

                        ("5. AGE AND LANGUAGE REQUIREMENTS", """
• No users under 13 years allowed!
• Only English and Italian languages please!
• Respect Discord's Terms of Service!"""),

                        ("⛔ SANCTIONS", """
Failure to comply with these rules will result in:
• 🟡 Warning
• 🔴 Temporary mute
• 🔴 Permanent ban for repeat offenses

By accepting these rules, you confirm you have read and accepted them.""")
                    ]
                    
                    for title, content in rules_sections:
                        embed.add_field(name=title, value=content, inline=False)
                    
                    embed.set_footer(text="Server Rules - English Version")
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento inglese inviato in #{channel.name}")
                    
                except discord.HTTPException as e:
                    print(f"❌ Errore HTTP regolamento inglese in #{channel.name}: {e}")
                    await self.send_rules_as_text(channel, "inglese")
                except Exception as e:
                    print(f"❌ Errore regolamento inglese in #{channel.name}: {e}")
                    await self.send_rules_as_text(channel, "inglese")

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
                        title="VERIFICA ACCOUNT / ACCOUNT VERIFICATION",
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
                        rules_refs += f"• **Regolamento Italiano:** {italian_channel.mention}\n"
                    if english_channel and self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        rules_refs += f"• **English Rules:** {english_channel.mention}\n"
                    
                    embed.add_field(
                        name="LEGGI IL REGOLAMENTO / READ THE RULES",
                        value=f"Prima di verificarti, leggi le regole:\n{rules_refs}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="SELEZIONA LINGUA / SELECT LANGUAGE",
                        value=(
                            "**Italiano** - Se sei italiano o preferisci l'italiano\n"
                            "**English** - Se preferisci l'inglese\n\n"
                            "La scelta determina la sezione del server che vedrai."
                        ),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="COMPLETA LA VERIFICA / COMPLETE VERIFICATION",
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
                            "**CLICCA IL PULSANTE PER VERIFICARTI**\n"
                            "**CLICK THE BUTTON TO VERIFY**"
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
        
        print(f"🔄 Comando setup_verify eseguito da {interaction.user.display_name}")
        self.verification_setup_done = False
        await self.setup_verification_system()
        
        await interaction.followup.send("✅ Regolamento e verifica re-inviati!", ephemeral=True)

    # COMANDO DI DEBUG
    @app_commands.command(name="debug_verify", description="Debug sistema verifica (Admin)")
    @app_commands.default_permissions(administrator=True)
    async def debug_verify(self, interaction: discord.Interaction):
        """Comando debug per verificare lo stato del sistema"""
        embed = discord.Embed(title="DEBUG SISTEMA VERIFICA", color=0x0099ff)
        
        # Informazioni canali
        embed.add_field(
            name="CONFIGURAZIONE CANALI",
            value=(
                f"**Canale Regole ITA:** `{self.ITALIAN_RULES_CHANNEL_ID}`\n"
                f"**Canale Regole ENG:** `{self.RULES_CHANNEL_ID}`\n"
                f"**Canale Verifica:** `{self.VERIFY_CHANNEL_ID}`\n"
                f"**Setup Completato:** `{self.verification_setup_done}`"
            ),
            inline=False
        )
        
        # Verifica canali nel server
        guild = interaction.guild
        ita_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
        eng_channel = guild.get_channel(self.RULES_CHANNEL_ID)
        verify_channel = guild.get_channel(self.VERIFY_CHANNEL_ID)
        
        embed.add_field(
            name="STATO CANALI NEL SERVER",
            value=(
                f"**ITA Channel:** {ita_channel.mention if ita_channel else '❌ NON TROVATO'}\n"
                f"**ENG Channel:** {eng_channel.mention if eng_channel else '❌ NON TROVATO'}\n"
                f"**Verify Channel:** {verify_channel.mention if verify_channel else '❌ NON TROVATO'}"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Inizia Verifica / Start Verification",
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
            title="Seleziona Lingua / Select Language",
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
            label="Italiano",
            style=discord.ButtonStyle.primary,
            custom_id="verify_ita"
        )
        
        eng_button = discord.ui.Button(
            label="English",
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
    print("✅ Cog VerificationSystem caricato!")
