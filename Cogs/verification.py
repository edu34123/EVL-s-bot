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
        
        # Ruoli - VERIFICA CHE QUESTI ID SIANO CORRETTI
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
        print("🌍 Sistema bilingue: Italiano & English")
        await asyncio.sleep(3)
        await self.setup_verification()

    async def setup_verification(self):
        """Configura i messaggi di verifica"""
        if self.verification_sent:
            return
            
        print("🔄 Setup sistema verifica bilingue...")
        
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
        print("✅ Setup completato! Gli utenti possono scegliere tra ITA e ENG")

    async def send_verification_message(self):
        """Invia il messaggio di verifica bilingue"""
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
                    
                    # EMBED BILINGUE MIGLIORATO
                    embed = discord.Embed(
                        title="🌍 VERIFICA ACCOUNT - SCEGLI LA LINGUA / ACCOUNT VERIFICATION - CHOOSE LANGUAGE",
                        color=0x00ff00
                    )
                    
                    # Descrizione chiara
                    embed.description = (
                        "**🇮🇹 Per utenti italiani o che preferiscono l'italiano**\n"
                        "**🇬🇧 For English users or those who prefer English**\n\n"
                        
                        "👉 **Scegli la lingua che preferisci per la tua esperienza nel server!**\n"
                        "👉 **Choose your preferred language for your server experience!**"
                    )
                    
                    # Benefici per ogni lingua
                    embed.add_field(
                        name="🇮🇹 SEZIONE ITALIANA",
                        value=(
                            "• Canali e chat in italiano\n"
                            "• Community italiana\n" 
                            "• Eventi e attività in italiano\n"
                            "• Supporto in lingua italiana"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🇬🇧 ENGLISH SECTION",
                        value=(
                            "• English channels and chats\n"
                            "• International community\n"
                            "• English events and activities\n"
                            "• English language support"
                        ),
                        inline=True
                    )
                    
                    # Istruzioni chiare
                    embed.add_field(
                        name="✅ COME VERIFICARSI / HOW TO VERIFY",
                        value=(
                            "1. **Clicca il pulsante sotto** / Click the button below\n"
                            "2. **Scegli la tua lingua** / Choose your language\n"
                            "3. **Completa la verifica** / Complete verification\n"
                            "4. **Accedi al server** / Access the server"
                        ),
                        inline=False
                    )
                    
                    embed.set_footer(text="Puoi cambiare lingua in qualsiasi momento / You can change language anytime")
                    
                    # Crea il pulsante principale
                    view = discord.ui.View(timeout=None)
                    view.add_item(VerifyButton())
                    
                    # Messaggio principale
                    await channel.send(
                        content=(
                            "**👇 CLICCA QUI PER SCEGLIERE LA LINGUA E VERIFICARTI 👇**\n"
                            "**👇 CLICK HERE TO CHOOSE YOUR LANGUAGE AND VERIFY 👇**"
                        ),
                        embed=embed,
                        view=view
                    )
                    
                    print(f"✅ Messaggio verifica bilingue inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio verifica: {e}")

    async def complete_verification(self, interaction: discord.Interaction, language: str):
        """Completa la verifica con la lingua scelta"""
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
            
            # Rimuovi ruolo unverified
            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
            
            # Aggiungi ruoli base
            roles_to_add = []
            if verified_role and verified_role not in member.roles:
                roles_to_add.append(verified_role)
            if fan_role and fan_role not in member.roles:
                roles_to_add.append(fan_role)
            
            # Gestione lingua
            if language == "ita" and ita_role:
                roles_to_add.append(ita_role)
                # Rimuovi inglese se presente
                if eng_role and eng_role in member.roles:
                    await member.remove_roles(eng_role)
            elif language == "eng" and eng_role:
                roles_to_add.append(eng_role)
                # Rimuovi italiano se presente
                if ita_role and ita_role in member.roles:
                    await member.remove_roles(ita_role)
            
            # Applica tutti i ruoli
            if roles_to_add:
                await member.add_roles(*roles_to_add)
            
            # Messaggio di conferma dettagliato
            if language == "ita":
                message = (
                    "✅ **Verifica completata con successo!** 🎉\n\n"
                    "**🇮🇹 Sezione Italiana attivata:**\n"
                    "• Accesso ai canali italiani\n"
                    "• Ruolo Fan assegnato\n"
                    "• Community italiana\n\n"
                    "Benvenuto nel server! 👋"
                )
            else:
                message = (
                    "✅ **Verification completed successfully!** 🎉\n\n"
                    "**🇬🇧 English Section activated:**\n"
                    "• Access to English channels\n"
                    "• Fan role assigned\n"
                    "• International community\n\n"
                    "Welcome to the server! 👋"
                )
            
            embed = discord.Embed(description=message, color=0x00ff00)
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            print(f"✅ {member.display_name} verificato - Lingua: {language}")
            
            # Messaggio di benvenuto nel canale generale (opzionale)
            try:
                system_channel = guild.system_channel
                if system_channel:
                    if language == "ita":
                        welcome_msg = f"🎉 **Benvenuto** {member.mention} nella **sezione italiana**! Dai il benvenuto! 👋"
                    else:
                        welcome_msg = f"🎉 **Welcome** {member.mention} to the **english section**! Say hello! 👋"
                    
                    await system_channel.send(welcome_msg, delete_after=30)
            except:
                pass
            
        except Exception as e:
            print(f"❌ Errore verifica: {e}")
            error_msg = (
                "❌ Errore durante la verifica. Riprova o contatta lo staff.\n"
                "❌ Error during verification. Try again or contact staff."
            )
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)

class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="🌍 Scegli Lingua / Choose Language",
            style=discord.ButtonStyle.success,
            custom_id="verify_choose_language",
            emoji="🌎"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Callback del pulsante di verifica"""
        cog = interaction.client.get_cog('Verification')
        if not cog:
            await interaction.response.send_message("❌ Sistema di verifica non disponibile", ephemeral=True)
            return
        
        # Embed di selezione lingua migliorato
        embed = discord.Embed(
            title="🌍 SCEGLI LA TUA LINGUA / CHOOSE YOUR LANGUAGE",
            color=0x0099ff
        )
        
        embed.description = (
            "**Seleziona la lingua che preferisci per la tua esperienza nel server:**\n"
            "**Select your preferred language for your server experience:**\n\n"
            
            "🇮🇹 **Italiano** - Se sei italiano o preferisci l'italiano\n"
            "🇬🇧 **English** - If you're English or prefer English\n\n"
            
            "💡 **La tua scelta determinerà:**\n"
            "• I canali che vedrai\n"
            "• La community con cui interagirai\n"
            "• Gli eventi a cui potrai partecipare\n\n"
            
            "🔁 Potrai cambiare lingua successivamente contattando lo staff."
        )
        
        # Pulsanti di selezione lingua
        view = discord.ui.View(timeout=180)
        
        # Pulsante Italiano
        ita_button = discord.ui.Button(
            label="🇮🇹 Italiano",
            style=discord.ButtonStyle.primary,
            custom_id="verify_italian",
            emoji="🇮🇹"
        )
        
        # Pulsante English
        eng_button = discord.ui.Button(
            label="🇬🇧 English", 
            style=discord.ButtonStyle.primary,
            custom_id="verify_english",
            emoji="🇬🇧"
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
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

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

async def setup(bot):
    await bot.add_cog(Verification(bot))
