import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands #  type: ignore
from config import VERIFIED_ROLE_ID, UNVERIFIED_ROLE_ID  # Importa dalla config # type: ignore

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="verify", description="Sistema di verifica")
    async def verify_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Verifica Account",
            description="Clicca il bottone qui sotto per verificare il tuo account!",
            color=0x00ff00
        )
        
        view = VerifyView()
        await interaction.response.send_message(embed=embed, view=view)

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verificati", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)  # Usa la costante
        unverified_role = interaction.guild.get_role(UNVERIFIED_ROLE_ID)  # Usa la costante
        
        if verified_role and unverified_role:
            if unverified_role in interaction.user.roles:
                await interaction.user.remove_roles(unverified_role)
            await interaction.user.add_roles(verified_role)
            
            embed = discord.Embed(
                title="Verifica Completata!",
                description="Sei stato verificato con successo!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Ruoli non configurati correttamente!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Verification(bot))