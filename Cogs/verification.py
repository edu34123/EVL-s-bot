import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione
        self.RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478'))
        self.ITALIAN_RULES_CHANNEL_ID = int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1392062840097210478'))
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
            
        print("🔄 Invio regolamenti e messaggi di verifica...")
        
        # Invio regolamenti
        if self.ITALIAN_RULES_CHANNEL_ID != 0:
            await self.send_italian_rules_message()
            await asyncio.sleep(2)
        
        if self.RULES_CHANNEL_ID != 0:
            await self.send_english_rules_message()
            await asyncio.sleep(2)
        
        # Messaggio di verifica
        if self.VERIFY_CHANNEL_ID != 0:
            await self.send_verification_message()
        
        self.verification_sent = True
        print("✅ Setup verifica completato!")

    async def send_italian_rules_message(self):
        """Invia il regolamento ITALIANO"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia messaggi vecchi
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO ITALIANO SEMPLIFICATO
                    embed = discord.Embed(
                        title="📜 REGOLAMENTO SERVER - ITALIANO 🇮🇹",
                        color=0x00ff00,
                        description="**Benvenuto nel server! Leggi attentamente il regolamento.**"
                    )
                    
                    rules_text = """
**1. RISPETTO**
- Sii educato con tutti
- No insulti o linguaggio offensivo
- Rispetta lo staff

**2. CONTENUTI**
- No contenuti NSFW/18+
- No spam o flood
- No informazioni personali

**3. COMUNICAZIONE**
- Usa i canali appropriati
- No off-topic
- Segui le indicazioni staff

**4. SANZIONI**
- Avvertimento → Mute → Ban

Accettando, confermi di aver letto le regole.
"""
                    
                    embed.add_field(name="Regole Complete", value=rules_text, inline=False)
                    embed.set_footer(text="Regolamento Italiano")
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento italiano inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore regolamento italiano: {e}")

    async def send_english_rules_message(self):
        """Invia il regolamento INGLESE"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.RULES_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia solo se canale diverso
                    if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        async for message in channel.history(limit=10):
                            if message.author == self.bot.user:
                                await message.delete()
                                await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # REGOLAMENTO INGLESE SEMPLIFICATO
                    embed = discord.Embed(
                        title="📜 SERVER RULES - ENGLISH 🇬🇧",
                        color=0x0099ff,
                        description="**Welcome to the server! Please read the rules carefully.**"
                    )
                    
                    rules_text = """
**1. RESPECT**
- Be polite to everyone
- No insults or offensive language
- Respect staff

**2. CONTENT**
- No NSFW/18+ content
- No spam or flooding
- No personal information

**3. COMMUNICATION**
- Use appropriate channels
- No off-topic
- Follow staff instructions

**4. SANCTIONS**
- Warning → Mute → Ban

By accepting, you confirm you've read the rules.
"""
                    
                    embed.add_field(name="Complete Rules", value=rules_text, inline=False)
                    embed.set_footer(text="Server Rules - English")
                    
                    await channel.send(embed=embed)
                    print(f"✅ Regolamento inglese inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore regolamento inglese: {e}")

    async def send_verification_message(self):
        """Invia UN SOLO messaggio di verifica bilingue"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.VERIFY_CHANNEL_ID)
            if channel:
                try:
                    # Pulizia messaggi vecchi
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                            await asyncio.sleep(0.5)
                    
                    await asyncio.sleep(2)
                    
                    # UN SOLO EMBED BILINGUE
                    embed = discord.Embed(
                        title="✅ VERIFICA ACCOUNT / ACCOUNT VERIFICATION",
                        color=0xffff00
                    )
                    
                    # Descrizione bilingue
                    embed.description = (
                        "**Benvenuto nel server!** 🇮🇹\n"
                        "**Welcome to the server!** 🇬🇧\n\n"
                        
                        "Per accedere a tutte le funzionalità, completa la verifica.\n"
                        "To access all features, complete the verification."
                    )
                    
                    # Riferimenti ai canali regolamento
                    rules_text = ""
                    italian_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                    english_channel = guild.get_channel(self.RULES_CHANNEL_ID)
                    
                    if italian_channel:
                        rules_text += f"• 🇮🇹 **Regolamento Italiano:** {italian_channel.mention}\n"
                    if english_channel and self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                        rules_text += f"• 🇬🇧 **English Rules:** {english_channel.mention}\n"
                    
                    embed.add_field(
                        name="📜 LEGGI IL REGOLAMENTO / READ THE RULES",
                        value=f"Prima di verificarti, leggi le regole:\nBefore verifying, read the rules:\n\n{rules_text}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🌍 SELEZIONA LINGUA / SELECT LANGUAGE", 
                        value=(
                            "**Italiano** - Per utenti italiani o che preferiscono l'italiano\n"
                            "**English** - For English users or those who prefer English\n\n"
                            "La scelta determina quale sezione del server vedrai.\n"
                            "The choice determines which server section you'll see."
                        ),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="✅ COMPLETA LA VERIFICA / COMPLETE VERIFICATION",
                        value=(
                            "Clicca il pulsante sotto per accettare le regole.\n"
                            "Click the button below to accept the rules."
                        ),
                        inline=False
                    )
                    
                    embed.set_footer(text="Verifica richiesta / Verification required")
                    
                    # Crea la view con il pulsante
                    view = discord.ui.View(timeout=None)
                    view.add_item(VerifyButton())
                    
                    # Invia UN SOLO messaggio
                    await channel.send(
                        content=(
                            "**👇 CLICCA PER VERIFICARTI / CLICK TO VERIFY 👇**\n"
                            "**🎯 Inizia Verifica / Start Verification**"
                        ),
                        embed=embed,
                        view=view
                    )
                    
                    print(f"✅ Messaggio verifica inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio verifica: {e}")

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
            if verified_role:
                await member.add_roles(verified_role)
            if fan_role:
                await member.add_roles(fan_role)
            
            # Gestione lingua
            if language == "ita" and ita_role:
                await member.add_roles(ita_role)
                if eng_role and eng_role in member.roles:
                    await member.remove_roles(eng_role)
            elif language == "eng" and eng_role:
                await member.add_roles(eng_role)
                if ita_role and ita_role in member.roles:
                    await member.remove_roles(ita_role)
            
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
            error_msg = "❌ Errore. Contatta lo staff. / Error. Contact staff."
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)

class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🎯 Inizia Verifica / Start Verification",
            style=discord.ButtonStyle.success,
            custom_id="verify_start_button"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback del pulsante di verifica"""
        cog = interaction.client.get_cog('Verification')
        if not cog:
            await interaction.response.send_message("❌ Sistema di verifica non disponibile", ephemeral=True)
            return
        
        member = interaction.user
        guild = interaction.guild
        verified_role = guild.get_role(cog.VERIFIED_ROLE_ID)
        
        if verified_role and verified_role in member.roles:
            await interaction.response.send_message(
                "❌ Sei già verificato! / You are already verified!",
                ephemeral=True
            )
            return
        
        # Crea l'embed di selezione lingua
        embed = discord.Embed(
            title="🌍 Seleziona Lingua / Select Language",
            color=0x0099ff,
            description=(
                "**Sei italiano o preferisci l'italiano?** → Clicca **Italiano**\n"
                "**Are you English or prefer English?** → Click **English**\n\n"
                "La scelta determina la sezione del server che vedrai.\n"
                "The choice determines which server section you'll see."
            )
        )
        
        # Crea i pulsanti per la lingua
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
    await bot.add_cog(Verification(bot))
