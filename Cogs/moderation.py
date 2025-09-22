import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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

async def setup(bot):
    await bot.add_cog(Moderation(bot))
