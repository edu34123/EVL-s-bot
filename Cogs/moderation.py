import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
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
    
    @app_commands.command(name="clear", description="Cancella messaggi")
    @app_commands.describe(amount="Numero di messaggi da cancellare")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount > 100:
            await interaction.response.send_message("Puoi cancellare massimo 100 messaggi!", ephemeral=True)
            return
        
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🗑️ Cancellati {amount} messaggi!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))