import discord
from discord import app_commands
from discord.ext import commands

class Partnership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="partnership", description="Crea una partnership")
    @app_commands.describe(
        server_name="Nome del server",
        description="Descrizione della partnership",
        invite_link="Link d'invito"
    )
    async def partnership(self, interaction: discord.Interaction, server_name: str, description: str, invite_link: str):
        from main import PARTNERSHIP_CHANNEL_ID
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Non hai i permessi necessari!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🤝 Partnership con {server_name}",
            description=description,
            color=0x9B59B6
        )
        embed.add_field(name="🔗 Link", value=invite_link, inline=False)
        embed.set_footer(text=f"Partnership creata da {interaction.user}")
        
        channel = self.bot.get_channel(PARTNERSHIP_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
            await interaction.response.send_message("Partnership creata con successo!", ephemeral=True)
        else:
            await interaction.response.send_message("Canale partnership non trovato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Partnership(bot))
