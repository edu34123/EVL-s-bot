import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione - VERIFICA QUESTI ID
        self.RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regole inglese
        self.ITALIAN_RULES_CHANNEL_ID = int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1392062840097210478'))  # Canale regole italiano
        self.VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID', '1392062838197059644'))  # Canale verifica
        
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
        print(f"📋 Canale Regole ITA: {self.ITALIAN_RULES_CHANNEL_ID}")
        print(f"📋 Canale Regole ENG: {self.RULES_CHANNEL_ID}")
        print(f"✅ Canale Verifica: {self.VERIFY_CHANNEL_ID}")
        
        # Aspetta che il bot sia completamente pronto
        await asyncio.sleep(5)
        await self.setup_verification()

    async def setup_verification(self):
        """Configura TUTTI i messaggi di verifica"""
        if self.verification_sent:
            print("⚠️ Messaggi già inviati, salto...")
            return
            
        print("🔄 INIZIO SETUP SISTEMA VERIFICA...")
        
        try:
            # 1. PRIMA invia il REGOLAMENTO ITALIANO
            if self.ITALIAN_RULES_CHANNEL_ID != 0:
                print("📜 Invio regolamento italiano...")
                await self.send_italian_rules_message()
                await asyncio.sleep(3)
            else:
                print("❌ Canale regolamento italiano non configurato")
            
            # 2. POI invia il REGOLAMENTO INGLESE
            if self.RULES_CHANNEL_ID != 0:
                print("📜 Invio regolamento inglese...")
                await self.send_english_rules_message()
                await asyncio.sleep(3)
            else:
                print("❌ Canale regolamento inglese non configurato")
            
            # 3. INFINE invia il MESSAGGIO di VERIFICA
            if self.VERIFY_CHANNEL_ID != 0:
                print("✅ Invio messaggio verifica...")
                await self.send_verification_message()
                await asyncio.sleep(2)
            else:
                print("❌ Canale verifica non configurato")
            
            self.verification_sent = True
            print("🎉 SETUP COMPLETATO! Tutti i messaggi inviati!")
            
        except Exception as e:
            print(f"❌ ERRORE durante setup verifica: {e}")

    async def send_italian_rules_message(self):
        """Invia il regolamento ITALIANO"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
            if channel:
                try:
                    print(f"🔄 Pulizia canale regolamento italiano: #{channel.name}")
                    # Pulizia messaggi vecchi del bot
                    deleted = 0
                    async for message in channel.history(limit=20):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                                deleted += 1
                                await asyncio.sleep(0.5)
                            except:
                                pass
                    
                    if deleted > 0:
                        print(f"🗑️ Eliminati {deleted} messaggi vecchi")
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO ITALIANO
                    embed = discord.Embed(
                        title="📜 REGOLAMENTO SERVER - ITALIANO 🇮🇹",
                        color=0x00ff00,
                        description="**Benvenuto nel server! Leggi attentamente il regolamento prima di partecipare.**"
                    )
                    
                    rules_text = """
**1. RISPETTO RECIPROCO**
• Sii rispettoso verso tutti i membri
• No insulti, discriminazioni o hate speech
• Mantieni un linguaggio educato

**2. CONTENUTI APPROPRIATI**
• No spam o flood di messaggi
• No contenuti NSFW/18+
• No condivisione di informazioni personali

**3. CANALI APPROPRIATI**
• Usa i canali per lo scopo previsto
• No off-topic nei canali dedicati
• Segui le indicazioni dello staff

**4. VOCE E VIDEO**
• No disturbi volontari in chat vocale
• No urla o rumori molesti
• Rispetta chi sta parlando

**⛔ SANZIONI**
Il mancato rispetto delle regole comporterà:
• 🟡 Avvertimento
• 🔴 Mute temporaneo  
• 🔴 Ban permanente per recidiva

Accettando queste regole, confermi di averle lette e accettate.
"""
                    
                    embed.add_field(name="Regolamento Completo", value=rules_text, inline=False)
                    embed.set_footer(text="Regolamento Server Italiano")
                    embed.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento ITALIANO inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento italiano: {e}")
            else:
                print(f"❌ Canale regolamento italiano non trovato (ID: {self.ITALIAN_RULES_CHANNEL_ID})")

    async def send_english_rules_message(self):
        """Invia il regolamento INGLESE"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia solo se canale diverso da italiano
                    if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        print(f"🔄 Pulizia canale regolamento inglese: #{channel.name}")
                        deleted = 0
                        async for message in channel.history(limit=10):
                            if message.author == self.bot.user:
                                try:
                                    await message.delete()
                                    deleted += 1
                                    await asyncio.sleep(0.5)
                                except:
                                    pass
                        
                        if deleted > 0:
                            print(f"🗑️ Eliminati {deleted} messaggi vecchi")
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO INGLESE
                    embed = discord.Embed(
                        title="📜 SERVER RULES - ENGLISH 🇬🇧",
                        color=0x0099ff,
                        description="**Welcome to the server! Please read the rules carefully before participating.**"
                    )
                    
                    rules_text = """
**1. MUTUAL RESPECT**
• Be respectful to all members
• No insults, discrimination or hate speech
• Maintain polite language

**2. APPROPRIATE CONTENT**
• No spam or message flooding
• No NSFW/18+ content
• No sharing personal information

**3. PROPER CHANNELS**
• Use channels for their intended purpose
• No off-topic in dedicated channels
• Follow staff instructions

**4. VOICE AND VIDEO**
• No intentional disturbances in voice chat
• No screaming or annoying noises
• Respect who is speaking

**⛔ SANCTIONS**
Failure to comply with rules will result in:
• 🟡 Warning
• 🔴 Temporary mute
• 🔴 Permanent ban for repeat offenses

By accepting these rules, you confirm you have read and accepted them.
"""
                    
                    embed.add_field(name="Complete Rules", value=rules_text, inline=False)
                    embed.set_footer(text="Server Rules - English Version")
                    embed.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento INGLESE inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento inglese: {e}")
            else:
                print(f"❌ Canale regolamento inglese non trovato (ID: {self.RULES_CHANNEL_ID})")

    async def send_verification_message(self):
        """Invia il messaggio di VERIFICA"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.VERIFY_CHANNEL_ID)
            if channel:
                try:
                    print(f"🔄 Pulizia canale verifica: #{channel.name}")
                    # Pulizia messaggi vecchi del bot
                    deleted = 0
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                                deleted += 1
                                await asyncio.sleep(0.5)
                            except:
                                pass
                    
                    if deleted > 0:
                        print(f"🗑️ Eliminati {deleted} messaggi vecchi")
                    
                    await asyncio.sleep(2)
                    
                    # MESSAGGIO DI VERIFICA
                    embed = discord.Embed(
                        title="✅ VERIFICA ACCOUNT / ACCOUNT VERIFICATION",
                        color=0xffff00
                    )
                    
                    embed.description = (
                        "**Benvenuto nel server!** 🇮🇹\n"
                        "**Welcome to the server!** 🇬🇧\n\n"
                        
                        "Per accedere a tutte le funzionalità del server, devi completare la verifica.\n"
                        "To access all server features, you need to complete verification."
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
                    
                    # Crea la view con il pulsante
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
                    
                    print(f"✅ Messaggio di VERIFICA inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio messaggio verifica: {e}")
            else:
                print(f"❌ Canale verifica non trovato (ID: {self.VERIFY_CHANNEL_ID})")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_verify(self, ctx):
        """Comando per forzare il setup della verifica"""
        self.verification_sent = False
        await ctx.send("🔄 Reinvio messaggi di verifica...")
        await self.setup_verification()
        await ctx.send("✅ Setup verifica completato!")

    # COMANDI SLASH
    @app_commands.command(name="verify", description="Completa la verifica del server")
    @app_commands.describe(language="Seleziona la tua lingua preferita")
    @app_commands.choices(language=[
        app_commands.Choice(name="🇮🇹 Italiano", value="ita"),
        app_commands.Choice(name="🇬🇧 English", value="eng")
    ])
    async def verify_command(self, interaction: discord.Interaction, language: app_commands.Choice[str]):
        """Comando slash per la verifica"""
        await self.complete_verification(interaction, language.value)

    async def complete_verification(self, interaction: discord.Interaction, language: str):
        """Completa la verifica"""
        member = interaction.user
        guild = interaction.guild
        
        # Verifica se già verificato
        verified_role = guild.get_role(self.VERIFIED_ROLE_ID)
        if verified_role and verified_role in member.roles:
            await interaction.response.send_message(
                "❌ Sei già verificato! / You are already verified!",
                ephemeral=True
            )
            return
        
        try:
            # Ruoli
            unverified_role = guild.get_role(self.UNVERIFIED_ROLE_ID)
            verified_role = guild.get_role(self.VERIFIED_ROLE_ID)
            fan_role = guild.get_role(self.FAN_ROLE_ID)
            ita_role = guild.get_role(self.ITA_ROLE_ID)
            eng_role = guild.get_role(self.ENG_ROLE_ID)
            
            # Rimuovi unverified
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
            
            # Aggiungi verified e fan
            roles_to_add = []
            if verified_role and verified_role not in member.roles:
                roles_to_add.append(verified_role)
            if fan_role and fan_role not in member.roles:
                roles_to_add.append(fan_role)
            
            # Gestione lingua
            if language == "ita" and ita_role:
                roles_to_add.append(ita_role)
                if eng_role and eng_role in member.roles:
                    await member.remove_roles(eng_role)
            elif language == "eng" and eng_role:
                roles_to_add.append(eng_role)
                if ita_role and ita_role in member.roles:
                    await member.remove_roles(ita_role)
            
            # Applica ruoli
            if roles_to_add:
                await member.add_roles(*roles_to_add)
            
            # Messaggio di conferma
            if language == "ita":
                message = "✅ **Verifica completata!** Sezione Italiana attivata. Benvenuto! 🎉"
            else:
                message = "✅ **Verification completed!** English Section activated. Welcome! 🎉"
            
            embed = discord.Embed(description=message, color=0x00ff00)
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            print(f"✅ {member.display_name} verificato ({language})")
            
        except Exception as e:
            print(f"❌ Errore verifica: {e}")
            error_msg = "❌ Errore durante la verifica. Contatta lo staff."
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)

class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🎯 Inizia Verifica / Start Verification",
            style=discord.ButtonStyle.success,
            custom_id="verify_start_button",
            emoji="✅"
        )
    
    async def callback(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog('Verification')
        if not cog:
            await interaction.response.send_message("❌ Sistema di verifica non disponibile", ephemeral=True)
            return
        
        # Embed selezione lingua
        embed = discord.Embed(
            title="🌍 Scegli Lingua / Choose Language",
            color=0x0099ff,
            description="Seleziona la tua lingua preferita / Select your preferred language"
        )
        
        view = discord.ui.View(timeout=180)
        
        # Pulsante Italiano
        ita_btn = discord.ui.Button(
            label="🇮🇹 Italiano",
            style=discord.ButtonStyle.primary,
            custom_id="verify_ita"
        )
        
        # Pulsante English
        eng_btn = discord.ui.Button(
            label="🇬🇧 English",
            style=discord.ButtonStyle.primary, 
            custom_id="verify_eng"
        )
        
        async def ita_callback(interaction):
            await cog.complete_verification(interaction, "ita")
        
        async def eng_callback(interaction):
            await cog.complete_verification(interaction, "eng")
        
        ita_btn.callback = ita_callback
        eng_btn.callback = eng_callback
        
        view.add_item(ita_btn)
        view.add_item(eng_btn)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Verification(bot))
