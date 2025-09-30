import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.WARN_CHANNEL_ID = int(os.getenv('WARN_CHANNEL_ID', '1409889529879330907'))
        self.WARN_ROLE_1_ID = int(os.getenv('WARN_ROLE_1_ID', '1403679881333706823'))
        self.WARN_ROLE_2_ID = int(os.getenv('WARN_ROLE_2_ID', '1403679930885345310')) 
        self.WARN_ROLE_3_ID = int(os.getenv('WARN_ROLE_3_ID', '1403679970886291497'))
    
    @app_commands.command(name="ban", description="Banna un utente")
    @app_commands.describe(user="Utente da bannare", reason="Motivo del ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Nessun motivo fornito"):
        await user.ban(reason=reason)
        
        embed = discord.Embed(
            title="Utente Bannato",
            description=f"{user.mention} è stato bannato da {interaction.user.mention}",
            color=0xff0000
        )
        embed.add_field(name="Motivo", value=reason)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="kick", description="Espelli un utente")
    @app_commands.describe(user="Utente da espellere", reason="Motivo dell'espulsione")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Nessun motivo fornito"):
        await user.kick(reason=reason)
        
        embed = discord.Embed(
            title="Utente Espulso",
            description=f"{user.mention} è stato espulso da {interaction.user.mention}",
            color=0xff9900
        )
        embed.add_field(name="Motivo", value=reason)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="timeout", description="Metti in timeout un utente")
    @app_commands.describe(user="Utente da mettere in timeout", minutes="Durata in minuti", reason="Motivo")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str = "Nessun motivo fornito"):
        duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await user.timeout(duration, reason=reason)
        
        embed = discord.Embed(
            title="Timeout Applicato",
            description=f"{user.mention} è in timeout per {minutes} minuti",
            color=0xffff00
        )
        embed.add_field(name="Motivo", value=reason)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clear", description="Cancella messaggi")
    @app_commands.describe(amount="Numero di messaggi da cancellare")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount > 100:
            await interaction.response.send_message("Puoi cancellare massimo 100 messaggi!", ephemeral=True)
            return
        
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🗑️ Cancellati {amount} messaggi!", ephemeral=True)
    
    @app_commands.command(name="unban", description="Sbanna un utente")
    @app_commands.describe(user_id="ID dell'utente da sbannare")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user_id = int(user_id)
            user = discord.Object(id=user_id)
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ Utente <@{user_id}> sbannato!")
        except ValueError:
            await interaction.response.send_message("ID utente non valido!", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("Utente non bannato!", ephemeral=True)
    
    @app_commands.command(name="warn", description="Avverti un utente")
    @app_commands.describe(
        user="Utente da avvertire",
        reason="Motivo dell'avvertimento (obbligatorio)"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Sistema di warn con ruoli progressivi"""
        try:
            # Conta i warn attuali dell'utente
            warn_count = await self.count_user_warns(user.id)
            new_warn_count = warn_count + 1
            
            # Assegna il ruolo warn appropriato
            await self.assign_warn_role(user, new_warn_count)
            
            # Invia il warn nel canale dedicato
            await self.send_warn_log(interaction, user, reason, new_warn_count)
            
            # Risposta all'staff
            embed = discord.Embed(
                title="⚠️ Warn Applicato",
                color=0xff9900,
                description=f"**Utente:** {user.mention}\n**Warn:** {new_warn_count}/3\n**Motivo:** {reason}"
            )
            embed.set_footer(text=f"Moderatore: {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
            # Avvisa l'utente
            try:
                user_embed = discord.Embed(
                    title="⚠️ Sei stato avvertito",
                    color=0xff9900,
                    description=f"Hai ricevuto un warn nel server **{interaction.guild.name}**"
                )
                user_embed.add_field(name="Motivo", value=reason, inline=False)
                user_embed.add_field(name="Warn Attuale", value=f"{new_warn_count}/3", inline=False)
                user_embed.add_field(name="Conseguenze", value=self.get_warn_consequences(new_warn_count), inline=False)
                
                await user.send(embed=user_embed)
            except discord.Forbidden:
                print(f"Impossibile inviare DM a {user.display_name}")
            
            # Se è il 3° warn, kick automatico
            if new_warn_count >= 3:
                await user.kick(reason=f"Raggiunto il 3° warn. Ultimo motivo: {reason}")
                
                kick_embed = discord.Embed(
                    title="🚨 Utente Kickato Automaticamente",
                    color=0xff0000,
                    description=f"{user.mention} è stato kickato per aver raggiunto 3 warn"
                )
                kick_embed.add_field(name="Ultimo Motivo", value=reason, inline=False)
                await interaction.followup.send(embed=kick_embed)
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore durante il warn: {e}", ephemeral=True)
    
    async def count_user_warns(self, user_id: int) -> int:
        """Conta i warn di un utente in base ai ruoli"""
        # In una versione più avanzata, potresti usare un database
        # Per ora contiamo in base ai ruoli presenti
        guild = self.bot.get_guild(interaction.guild.id)  # Usa il guild dell'interaction
        
        if not guild:
            return 0
            
        member = guild.get_member(user_id)
        if not member:
            return 0
        
        warn_count = 0
        if self.WARN_ROLE_1_ID in [role.id for role in member.roles]:
            warn_count = 1
        if self.WARN_ROLE_2_ID in [role.id for role in member.roles]:
            warn_count = 2
        if self.WARN_ROLE_3_ID in [role.id for role in member.roles]:
            warn_count = 3
            
        return warn_count
    
    async def assign_warn_role(self, user: discord.Member, warn_count: int):
        """Assegna il ruolo warn appropriato"""
        guild = user.guild
        
        # Rimuovi tutti i ruoli warn precedenti
        warn_roles = [self.WARN_ROLE_1_ID, self.WARN_ROLE_2_ID, self.WARN_ROLE_3_ID]
        for role_id in warn_roles:
            role = guild.get_role(role_id)
            if role and role in user.roles:
                await user.remove_roles(role)
        
        # Assegna il nuovo ruolo warn
        if warn_count == 1:
            role = guild.get_role(self.WARN_ROLE_1_ID)
        elif warn_count == 2:
            role = guild.get_role(self.WARN_ROLE_2_ID)
        elif warn_count >= 3:
            role = guild.get_role(self.WARN_ROLE_3_ID)
        else:
            return
        
        if role:
            await user.add_roles(role)
    
    async def send_warn_log(self, interaction: discord.Interaction, user: discord.Member, reason: str, warn_count: int):
        """Invia il log del warn nel canale dedicato"""
        channel = interaction.guild.get_channel(self.WARN_CHANNEL_ID)
        if not channel:
            return
        
        embed = discord.Embed(
            title="📝 Nuovo Warn Registrato",
            color=0xff9900,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="👤 Utente", value=f"{user.mention} (`{user.id}`)", inline=True)
        embed.add_field(name="🔢 Warn", value=f"{warn_count}/3", inline=True)
        embed.add_field(name="🛡️ Moderatore", value=interaction.user.mention, inline=True)
        embed.add_field(name="📋 Motivo", value=reason, inline=False)
        embed.add_field(name="⚠️ Conseguenze", value=self.get_warn_consequences(warn_count), inline=False)
        
        await channel.send(embed=embed)
    
    def get_warn_consequences(self, warn_count: int) -> str:
        """Restituisce le conseguenze del warn"""
        consequences = {
            1: "• Ruolo Warn 1 assegnato\n• Monitoraggio comportamento",
            2: "• Ruolo Warn 2 assegnato\n• Limitazioni aggiuntive\n• Ultimo avvertimento",
            3: "• Ruolo Warn 3 assegnato\n• **KICK AUTOMATICO**\n• Possibile ban al rientro"
        }
        return consequences.get(warn_count, "Nessuna conseguenza specifica")
    
    @app_commands.command(name="warns", description="Controlla i warn di un utente")
    @app_commands.describe(user="Utente da controllare")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warns(self, interaction: discord.Interaction, user: discord.Member):
        """Mostra i warn di un utente"""
        warn_count = await self.count_user_warns(user.id)
        
        embed = discord.Embed(
            title=f"⚠️ Warn di {user.display_name}",
            color=0xff9900
        )
        embed.add_field(name="Warn Attuali", value=f"{warn_count}/3", inline=True)
        embed.add_field(name="Stato", value=self.get_warn_status(warn_count), inline=True)
        embed.add_field(name="Conseguenze", value=self.get_warn_consequences(warn_count), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def get_warn_status(self, warn_count: int) -> str:
        """Restituisce lo stato del warn"""
        status = {
            0: "✅ Nessun warn",
            1: "⚠️ Primo warn",
            2: "🚨 Secondo warn",
            3: "🔴 Terzo warn (KICK)"
        }
        return status.get(warn_count, "Sconosciuto")
    
    @app_commands.command(name="removewarn", description="Rimuovi un warn da un utente")
    @app_commands.describe(user="Utente a cui rimuovere il warn")
    @app_commands.checks.has_permissions(administrator=True)
    async def removewarn(self, interaction: discord.Interaction, user: discord.Member):
        """Rimuovi un warn da un utente"""
        try:
            current_warns = await self.count_user_warns(user.id)
            if current_warns == 0:
                await interaction.response.send_message("❌ Questo utente non ha warn!", ephemeral=True)
                return
            
            new_warn_count = current_warns - 1
            await self.assign_warn_role(user, new_warn_count)
            
            embed = discord.Embed(
                title="✅ Warn Rimosso",
                color=0x00ff00,
                description=f"**Utente:** {user.mention}\n**Warn Precedenti:** {current_warns}\n**Warn Attuali:** {new_warn_count}"
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore nella rimozione del warn: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
