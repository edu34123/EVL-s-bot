import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class TicketSystemITA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}
        print("✅ TicketSystemITA inizializzato!")

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Sistema Ticket ITALIANO caricato!")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        """Crea un ticket in italiano"""
        try:
            guild = interaction.guild
            member = interaction.user
            
            print(f"🎯 Creando ticket ITALIANO: {ticket_type} per {member.display_name}")
            
            # Crea il canale ticket
            category = interaction.channel.category
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, manage_channels=True)
            }
            
            ticket_channel = await category.create_text_channel(
                name=f"ticket-ita-{ticket_type}-{member.display_name}",
                overwrites=overwrites
            )
            
            # Embed in italiano
            embed = discord.Embed(
                title=f"🎫 Ticket {ticket_type.capitalize()} - Italiano",
                color=0x00ff00,
                description=f"**Aperto da:** {member.mention}\n**Tipo:** {ticket_type.capitalize()}\n**Lingua:** 🇮🇹 Italiano"
            )
            
            embed.add_field(
                name="📜 Regole del Ticket",
                value="• Non taggare lo staff\n• Ticket chiuso dopo 24h\n• Sii chiaro e conciso",
                inline=False
            )
            
            # Pulsanti in italiano
            class TicketViewITA(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                
                @discord.ui.button(label="🎯 Claim", style=discord.ButtonStyle.success, custom_id="claim_ita")
                async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_message("✅ Ticket claimato! (ITA)", ephemeral=True)
                
                @discord.ui.button(label="🔒 Chiudi", style=discord.ButtonStyle.danger, custom_id="close_ita")
                async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_message("✅ Ticket chiuso! (ITA)", ephemeral=True)
            
            await ticket_channel.send(
                f"**Nuovo ticket {ticket_type} in italiano** - {member.mention}",
                embed=embed, 
                view=TicketViewITA()
            )
            
            await interaction.response.send_message(
                f"✅ Ticket italiano creato! Vai in {ticket_channel.mention}",
                ephemeral=True
            )
            
            print(f"✅ Ticket ITA creato: {ticket_channel.name}")
            
        except Exception as e:
            error_msg = f"❌ Errore creazione ticket ITA: {str(e)}"
            print(error_msg)
            await interaction.response.send_message(error_msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystemITA(bot))
    print("✅ TicketSystemITA caricato!")
