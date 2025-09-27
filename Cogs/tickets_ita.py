import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class TicketSystemITA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}
        self.STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID', '1394357096295956580'))
        self.PARTNERSHIP_ROLE_ID = int(os.getenv('PARTNERSHIP_ROLE_ID', '1408162707575803975'))
        self.SUPPORT_ROLE_ID = int(os.getenv('SUPPORT_ROLE_ID', '1392746082588557383'))
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
            
            # Staff può solo vedere inizialmente
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )
            
            ticket_channel = await category.create_text_channel(
                name=f"🎫-ita-{ticket_type}-{member.display_name}",
                overwrites=overwrites
            )
            
            # Salva info ticket
            self.open_tickets[ticket_channel.id] = {
                "owner": member.id,
                "type": ticket_type,
                "claimed_by": None,
                "language": "ita"
            }
            
            # RUOLO DA TAGGARE - CORREZIONE IMPORTANTE
            role_to_ping = None
            if ticket_type == "partnership":
                role_to_ping = guild.get_role(self.PARTNERSHIP_ROLE_ID)
            else:  # support
                role_to_ping = guild.get_role(self.SUPPORT_ROLE_ID)
            
            print(f"🔔 Ruolo da taggare: {role_to_ping.name if role_to_ping else 'Nessuno'}")
            
            # Embed in italiano
            embed = discord.Embed(
                title=f"🎫 Ticket {ticket_type.capitalize()} - Italiano",
                color=0x00ff00,
                description=f"**Aperto da:** {member.mention}\n**Tipo:** {ticket_type.capitalize()}\n**Lingua:** 🇮🇹 Italiano\n**Stato:** 🔓 In attesa di staff"
            )
            
            embed.add_field(
                name="📜 Regole del Ticket",
                value="• Non taggare lo staff, verranno automaticamente notificati\n• Ticket chiuso dopo 24h di inattività\n• Sii chiaro e conciso",
                inline=False
            )
            
            # MESSAGGIO DI PING CORRETTO
            ping_message = ""
            if role_to_ping:
                ping_message = f"{role_to_ping.mention} "  # TAGGARE IL RUOLO CORRETTO
            
            ping_message += f"**Nuovo ticket {ticket_type} in italiano** - {member.mention}"
            
            await ticket_channel.send(
                ping_message,  # MESSAGGIO CON TAGG
                embed=embed, 
                view=TicketViewITA(self, ticket_channel.id)
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

    # ... (resto del codice uguale per claim_ticket e close_ticket)

class TicketViewITA(discord.ui.View):
    def __init__(self, cog, ticket_channel_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.ticket_channel_id = ticket_channel_id
    
    @discord.ui.button(label="🎯 Claim", style=discord.ButtonStyle.success, custom_id="claim_ita")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role_id = int(os.getenv('STAFF_ROLE_ID', '1394357096295956580'))
        staff_role = interaction.guild.get_role(staff_role_id)
        
        if staff_role and staff_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Solo lo staff può claimare i ticket!", ephemeral=True)
            return
        
        await self.cog.claim_ticket(interaction, self.ticket_channel_id)
    
    @discord.ui.button(label="🔒 Chiudi", style=discord.ButtonStyle.danger, custom_id="close_ita")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket_info = self.cog.open_tickets.get(self.ticket_channel_id)
        if not ticket_info:
            await interaction.response.send_message("❌ Ticket non trovato!", ephemeral=True)
            return
        
        staff_role_id = int(os.getenv('STAFF_ROLE_ID', '1394357096295956580'))
        staff_role = interaction.guild.get_role(staff_role_id)
        
        is_staff = staff_role and staff_role in interaction.user.roles
        is_owner = ticket_info["owner"] == interaction.user.id
        is_claimer = ticket_info["claimed_by"] == interaction.user.id
        
        if not (is_staff or is_owner or is_claimer):
            await interaction.response.send_message("❌ Solo staff o il creatore può chiudere il ticket!", ephemeral=True)
            return
        
        await self.cog.close_ticket(interaction, self.ticket_channel_id)

async def setup(bot):
    await bot.add_cog(TicketSystemITA(bot))
    print("✅ TicketSystemITA caricato!")
