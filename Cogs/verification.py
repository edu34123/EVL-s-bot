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
            
        # Canale regolamento
        if self.RULES_CHANNEL_ID != 0:
            await self.send_rules_message()
        
        # Canale verifica
        if self.VERIFY_CHANNEL_ID != 0:
            await self.send_verification_message()
        
        self.verification_sent = True

    async def send_rules_message(self):
        """Invia il messaggio del regolamento"""
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
                    
                    # Embed regolamento italiano
                    embed_ita = discord.Embed(
                        title="📜 REGOLAMENTO SERVER - ITALIANO",
                        color=0x00ff00,
                        description="Benvenuto nel server! Per favore leggi attentamente il regolamento."
                    )
                    
                    rules_ita = """
**1. Non essere tossico con gli altri membri!**
**2. Nessun contenuto NSFW permesso!**
**3. Nessun contenuto gore!**
**4. Nessun insulto o linguaggio offensivo!**
**5. No spam!**
**6. Mention/Ping:**
   - Non pingare gli admin!
   - Solo persone con ruoli speciali possono essere pingate
**6.1. No ghost ping**
**7. Non condividere informazioni personali!**
   - Solo in <#1392062848414257204> 
**8. Nessuna immagine profilo o nome offensivo!**
**9. No impersonazione!**
**10. Nessun utente sotto i 13 anni permesso!**
**11. Lingua:**
   - Solo Italiano e Inglese per favore!
**12. Rispetta i Termini di Servizio di Discord!**
**13. Rispetta lo staff e le loro decisioni!**
**14. No pubblicità non autorizzata!**
**15. Usa i canali appropriati per ogni contenuto!**

Accettando queste regole, confermi di averle lette e accettate.
"""
                    
                    embed_ita.add_field(
                        name="Regole del Server",
                        value=rules_ita,
                        inline=False
                    )
                    
                    embed_ita.set_footer(text="Ultimo aggiornamento")
                    embed_ita.timestamp = discord.utils.utcnow()
                    
                    # Embed regolamento inglese
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
                    
                    embed_eng.set_footer(text="Last update")
                    embed_eng.timestamp = discord.utils.utcnow()
                    
                    await channel.send(embed=embed_ita)
                    await asyncio.sleep(1)
                    await channel.send(embed=embed_eng)
                    
                    print(f"✅ Regolamento inviato in #{channel.name}")
                    
                except Exception as e:
                    print(f"❌ Errore invio regolamento: {e}")

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
                    
                    embed_ita.add_field(
                        name="📜 Step 1: Leggi il Regolamento",
                        value="Assicurati di aver letto e compreso il regolamento del server.",
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

    @app_commands.command(name="setup_verification", description="Rigenera i messaggi di verifica (solo admin)")
    @app_commands.default_permissions(administrator=True)
    async def setup_verification_slash(self, interaction: discord.Interaction):
        """Comando slash per rigenerare la verifica"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Non hai i permessi per questo comando!", ephemeral=True)
            return
        
        self.verification_sent = False
        await self.setup_verification()
        await interaction.response.send_message("✅ Sistema verifica riconfigurato!", ephemeral=True)

    @app_commands.command(name="verify_user", description="Verifica manualmente un utente (solo admin)")
    @app_commands.describe(
        user="Utente da verificare",
        language="Lingua da assegnare"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="🇮🇹 Italiano", value="ita"),
        app_commands.Choice(name="🇬🇧 English", value="eng")
    ])
    @app_commands.default_permissions(administrator=True)
    async def verify_user_slash(self, interaction: discord.Interaction, user: discord.Member, language: app_commands.Choice[str]):
        """Comando slash per verificare manualmente un utente"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Non hai i permessi per questo comando!", ephemeral=True)
            return
        
        try:
            # Ruoli da gestire
            unverified_role = interaction.guild.get_role(self.UNVERIFIED_ROLE_ID)
            verified_role = interaction.guild.get_role(self.VERIFIED_ROLE_ID)
            fan_role = interaction.guild.get_role(self.FAN_ROLE_ID)
            ita_role = interaction.guild.get_role(self.ITA_ROLE_ID) if self.ITA_ROLE_ID != 0 else None
            eng_role = interaction.guild.get_role(self.ENG_ROLE_ID) if self.ENG_ROLE_ID != 0 else None
            
            # Rimuovi ruolo unverified
            if unverified_role and unverified_role in user.roles:
                await user.remove_roles(unverified_role)
            
            # Aggiungi ruolo verified
            if verified_role and verified_role not in user.roles:
                await user.add_roles(verified_role)
            
            # Aggiungi ruolo fan
            if fan_role and fan_role not in user.roles:
                await user.add_roles(fan_role)
            
            # Gestisci ruoli lingua
            roles_to_add = []
            roles_to_remove = []
            
            if language.value == "ita" and ita_role:
                roles_to_add.append(ita_role)
                if eng_role and eng_role in user.roles:
                    roles_to_remove.append(eng_role)
            elif language.value == "eng" and eng_role:
                roles_to_add.append(eng_role)
                if ita_role and ita_role in user.roles:
                    roles_to_remove.append(ita_role)
            
            # Applica i cambiamenti
            if roles_to_remove:
                await user.remove_roles(*roles_to_remove)
            if roles_to_add:
                await user.add_roles(*roles_to_add)
            
            await interaction.response.send_message(
                f"✅ **{user.display_name}** verificato correttamente per la sezione **{language.name}**!",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"❌ Errore verifica utente slash: {e}")
            await interaction.response.send_message("❌ Errore durante la verifica manuale!", ephemeral=True)

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
                message = "✅ **Verifica completata!** Sezione Italiana attivata. Benvenuto! 🎉"
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
