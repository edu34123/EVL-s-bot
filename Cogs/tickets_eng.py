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
            staff_role = guild.get_role(self.STAFF_ROLE_ID)
            
            # Permessi iniziali: staff può vedere ma non scrivere
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
            
            # Staff può solo vedere inizialmente
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,  # Non può scrivere inizialmente
                    read_message_history=True
                )
            
            ticket_channel = await category.create_text_channel(
                name=f"🎫-eng-{ticket_type}-{member.display_name}",
                overwrites=overwrites
            )
            
            # Salva info ticket
            self.open_tickets[ticket_channel.id] = {
                "owner": member.id,
                "type": ticket_type,
                "claimed_by": None,
                "language": "eng"
            }
            
            # Embed in inglese
            embed = discord.Embed(
                title=f"🎫 {ticket_type.capitalize()} Ticket - English",
                color=0x0099ff,
                description=f"**Opened by:** {member.mention}\n**Type:** {ticket_type.capitalize()}\n**Language:** 🇬🇧 English\n**Status:** 🔓 Waiting for staff"
            )
            
            embed.add_field(
                name="📜 Ticket Rules",
                value="• Don't ping staff\n• Ticket closed after 24h\n• Be clear and concise",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Available Actions",
                value="• **Claim** - Take over the ticket\n• **Close** - Close the ticket",
                inline=False
            )
            
            await ticket_channel.send(
                f"**New {ticket_type} ticket in English** - {member.mention}",
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

    async def claim_ticket(self, interaction: discord.Interaction, ticket_channel_id: int):
        """Claim the ticket - only claiming staff can write"""
        try:
            ticket_info = self.open_tickets.get(ticket_channel_id)
            if not ticket_info:
                await interaction.response.send_message("❌ Ticket not found!", ephemeral=True)
                return
            
            if ticket_info["claimed_by"]:
                await interaction.response.send_message("❌ Ticket already claimed!", ephemeral=True)
                return
            
            # Update permissions - only claiming staff can write
            channel = interaction.channel
            guild = interaction.guild
            staff_role = guild.get_role(self.STAFF_ROLE_ID)
            
            overwrites = channel.overwrites
            
            # Staff can only view
            if staff_role in overwrites:
                overwrites[staff_role].update(send_messages=False)
            
            # Claiming staff can write
            overwrites[interaction.user] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
            
            await channel.edit(overwrites=overwrites)
            
            # Update ticket info
            ticket_info["claimed_by"] = interaction.user.id
            self.open_tickets[ticket_channel_id] = ticket_info
            
            embed = discord.Embed(
                description=f"✅ **Ticket claimed by {interaction.user.mention}**\nNow only the claiming staff can write in this ticket.",
                color=0x00ff00
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error during claim: {e}", ephemeral=True)

    async def close_ticket(self, interaction: discord.Interaction, ticket_channel_id: int):
        """Close the ticket with confirmation"""
        try:
            ticket_info = self.open_tickets.get(ticket_channel_id)
            if not ticket_info:
                await interaction.response.send_message("❌ Ticket not found!", ephemeral=True)
                return
            
            embed = discord.Embed(
                description="🔒 **Ticket closed**\nThe ticket will be deleted in 10 seconds...",
                color=0xff0000
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Wait and delete
            await asyncio.sleep(10)
            await interaction.channel.delete()
            
            # Remove from open tickets
            if ticket_channel_id in self.open_tickets:
                del self.open_tickets[ticket_channel_id]
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Error during closing: {e}", ephemeral=True)

class TicketViewENG(discord.ui.View):
    def __init__(self, cog, ticket_channel_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.ticket_channel_id = ticket_channel_id
    
    @discord.ui.button(label="🎯 Claim", style=discord.ButtonStyle.success, custom_id="claim_eng")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verify staff role
        staff_role_id = int(os.getenv('STAFF_ROLE_ID', '1400000000000000003'))
        staff_role = interaction.guild.get_role(staff_role_id)
        
        if staff_role and staff_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Only staff can claim tickets!", ephemeral=True)
            return
        
        await self.cog.claim_ticket(interaction, self.ticket_channel_id)
    
    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.danger, custom_id="close_eng")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verify staff or ticket owner
        ticket_info = self.cog.open_tickets.get(self.ticket_channel_id)
        if not ticket_info:
            await interaction.response.send_message("❌ Ticket not found!", ephemeral=True)
            return
        
        staff_role_id = int(os.getenv('STAFF_ROLE_ID', '1394357096295956580'))
        staff_role = interaction.guild.get_role(staff_role_id)
        
        is_staff = staff_role and staff_role in interaction.user.roles
        is_owner = ticket_info["owner"] == interaction.user.id
        is_claimer = ticket_info["claimed_by"] == interaction.user.id
        
        if not (is_staff or is_owner or is_claimer):
            await interaction.response.send_message("❌ Only staff or ticket creator can close the ticket!", ephemeral=True)
            return
        
        await self.cog.close_ticket(interaction, self.ticket_channel_id)

async def setup(bot):
    await bot.add_cog(TicketSystemENG(bot))
    print("✅ TicketSystemENG caricato!")
