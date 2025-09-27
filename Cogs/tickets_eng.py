import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class TicketSystemENG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}
        print("✅ TicketSystemENG inizializzato!")

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Sistema Ticket INGLESE caricato!")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        """Crea un ticket in inglese"""
        try:
            guild = interaction.guild
            member = interaction.user
            
            print(f"🎯 Creando ticket INGLESE: {ticket_type} per {member.display_name}")
            
            # Crea il canale ticket
            category = interaction.channel.category
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
            }
            
            ticket_channel = await category.create_text_channel(
                name=f"ticket-eng-{ticket_type}-{member.display_name}",
                overwrites=overwrites
            )
            
            # Embed in inglese
            embed = discord.Embed(
                title=f"🎫 {ticket_type.capitalize()} Ticket - English",
                color=0x0099ff,
                description=f"**Opened by:** {member.mention}\n**Type:** {ticket_type.capitalize()}\n**Language:** 🇬🇧 English"
            )
            
            embed.add_field(
                name="📜 Ticket Rules",
                value="• Don't ping staff\n• Ticket closed after 24h\n• Be clear and concise",
                inline=False
            )
            
            # Pulsanti in inglese
            class TicketViewENG(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                
                @discord.ui.button(label="🎯 Claim", style=discord.ButtonStyle.success, custom_id="claim_eng")
                async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_message("✅ Ticket claimed! (ENG)", ephemeral=True)
                
                @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.danger, custom_id="close_eng")
                async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_message("✅ Ticket closed! (ENG)", ephemeral=True)
            
            await ticket_channel.send(
                f"**New {ticket_type} ticket in English** - {member.mention}",
                embed=embed, 
                view=TicketViewENG()
            )
            
            await interaction.response.send_message(
                f"✅ English ticket created! Go to {ticket_channel.mention}",
                ephemeral=True
            )
            
            print(f"✅ Ticket ENG creato: {ticket_channel.name}")
            
        except Exception as e:
            error_msg = f"❌ Error creating ENG ticket: {str(e)}"
            print(error_msg)
            await interaction.response.send_message(error_msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystemENG(bot))
    print("✅ TicketSystemENG caricato!")
