import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class TicketSystemENG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}
        self.STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID', '1394357096295956580'))
        self.PARTNERSHIP_ROLE_ID = int(os.getenv('PARTNERSHIP_ROLE_ID', '1408162707575803975'))
        self.SUPPORT_ROLE_ID = int(os.getenv('SUPPORT_ROLE_ID', '1392746082588557383'))
        print("✅ TicketSystemENG inizializzato!")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        """Crea un ticket in inglese"""
        try:
            guild = interaction.guild
            member = interaction.user
            
            print(f"🎯 Creando ticket INGLESE: {ticket_type} per {member.display_name}")
            
            # Crea il canale ticket
            category = interaction.channel.category
            staff_role = guild.get_role(self.STAFF_ROLE_ID)
            
            # Permessi iniziali
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(
                    view_channel=True, 
                    send_messages=True, 
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    view_channel=True, 
                    send_messages=True, 
                    manage_channels=True,
                    manage_messages=True
                )
            }
            
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )
            
            ticket_channel = await category.create_text_channel(
                name=f"🎫-eng-{ticket_type}-{member.display_name}",
                overwrites=overwrites
            )
            
            self.open_tickets[ticket_channel.id] = {
                "owner": member.id,
                "type": ticket_type,
                "claimed_by": None,
                "language": "eng"
            }
            
            # RUOLO DA TAGGARE
            role_to_ping = None
            if ticket_type == "partnership":
                role_to_ping = guild.get_role(self.PARTNERSHIP_ROLE_ID)
            else:  # support
                role_to_ping = guild.get_role(self.SUPPORT_ROLE_ID)
            
            print(f"🔔 Ruolo da taggare: {role_to_ping.name if role_to_ping else 'Nessuno'}")
            
            # Embed in inglese
            embed = discord.Embed(
                title=f"🎫 {ticket_type.capitalize()} Ticket - English",
                color=0x0099ff,
                description=f"**Opened by:** {member.mention}\n**Type:** {ticket_type.capitalize()}\n**Language:** 🇬🇧 English\n**Status:** 🔓 Waiting for staff"
            )
            
            # MESSAGGIO DI PING CORRETTO
            ping_message = ""
            if role_to_ping:
                ping_message = f"{role_to_ping.mention} "
            
            ping_message += f"**New {ticket_type} ticket in English** - {member.mention}"
            
            await ticket_channel.send(
                ping_message,
                embed=embed, 
                view=TicketViewENG(self, ticket_channel.id)
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

    # ... (resto del codice uguale)

async def setup(bot):
    await bot.add_cog(TicketSystemENG(bot))
    print("✅ TicketSystemENG caricato!")
