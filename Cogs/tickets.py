import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.open_tickets = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Sistema Ticket caricato!")
        self.bot.add_view(TicketCreationView())

    @app_commands.command(name="setup_tickets", description="Setup sistema ticket (Admin)")
    @app_commands.default_permissions(administrator=True)
    # In cogs/tickets.py - assicurati di avere questo metodo:
async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
    """Crea un nuovo ticket"""
    try:
        # ... il tuo codice per creare il ticket ...
        await interaction.response.send_message(f"✅ Ticket {ticket_type} creato!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
        
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup dei messaggi ticket"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # EMBED ITALIANO
            embed_ita = discord.Embed(
                title="🎫 SISTEMA TICKET - ITALIANO 🇮🇹",
                color=0x00ff00,
                description="**Apri un ticket per richiedere assistenza o partnership!**"
            )
            
            embed_ita.add_field(
                name="📋 Tipi di Ticket Disponibili",
                value="**🤝 Partnership** - Per collaborazioni e partnership\n**🛠️ Supporto** - Per assistenza e problemi tecnici",
                inline=False
            )
            
            embed_ita.add_field(
                name="📜 Regole Ticket",
                value="• Non taggare lo staff, verranno automaticamente notificati\n• Il ticket verrà chiuso dopo 24h di inattività\n• Sii chiaro e conciso nella tua richiesta\n• Rispetta lo staff e le sue decisioni",
                inline=False
            )
            
            # EMBED INGLESE
            embed_eng = discord.Embed(
                title="🎫 TICKET SYSTEM - ENGLISH 🇬🇧",
                color=0x0099ff,
                description="**Open a ticket to request assistance or partnership!**"
            )
            
            embed_eng.add_field(
                name="📋 Available Ticket Types",
                value="**🤝 Partnership** - For collaborations and partnerships\n**🛠️ Support** - For assistance and technical issues",
                inline=False
            )
            
            embed_eng.add_field(
                name="📜 Ticket Rules",
                value="• Don't ping staff, they will be automatically notified\n• Ticket will be closed after 24h of inactivity\n• Be clear and concise in your request\n• Respect staff and their decisions",
                inline=False
            )
            
            # Crea view per entrambe le lingue
            view = TicketCreationView()
            
            # Invia i messaggi
            await interaction.channel.send(embed=embed_ita, view=view)
            await interaction.channel.send(embed=embed_eng, view=view)
            
            await interaction.followup.send("✅ Sistema ticket configurato correttamente!", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Errore durante il setup: {e}", ephemeral=True)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        """Crea un nuovo ticket"""
        try:
            guild = interaction.guild
            member = interaction.user
            
            # Crea il canale ticket nella categoria corrente
            category = interaction.channel.category
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
            }
            
            # Crea il canale
            ticket_channel = await category.create_text_channel(
                name=f"ticket-{ticket_type}-{member.display_name}",
                overwrites=overwrites
            )
            
            # Salva informazioni del ticket
            self.open_tickets[ticket_channel.id] = {
                "owner": member.id,
                "type": ticket_type,
                "claimed_by": None
            }
            
            # Embed del ticket
            embed = discord.Embed(
                title=f"🎫 Ticket {ticket_type.capitalize()} - {member.display_name}",
                color=0x00ff00,
                description=f"**Ticket aperto da:** {member.mention}\n**Tipo:** {ticket_type.capitalize()}\n**Stato:** 🔓 In attesa di staff"
            )
            
            embed.add_field(
                name="📜 Regole del Ticket",
                value="• Non taggare lo staff, verranno automaticamente notificati\n• Il ticket verrà chiuso dopo 24h di inattività\n• Lo staff ti risponderà al più presto",
                inline=False
            )
            
            # Pulsanti di gestione
            view = TicketManagementView()
            
            await ticket_channel.send(
                content=f"📢 **Nuovo ticket {ticket_type}** - {member.mention}",
                embed=embed,
                view=view
            )
            
            await interaction.response.send_message(
                f"✅ Ticket creato correttamente! Vai in {ticket_channel.mention}",
                ephemeral=True
            )
            
            print(f"✅ Ticket creato: {ticket_channel.name}")
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore nella creazione del ticket: {e}", ephemeral=True)
            print(f"❌ Errore ticket: {e}")

class TicketCreationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🤝 Partnership", style=discord.ButtonStyle.primary, custom_id="ticket_partnership")
    async def partnership_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if cog:
            await cog.create_ticket(interaction, "partnership")
        else:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
    
    @discord.ui.button(label="🛠️ Supporto", style=discord.ButtonStyle.secondary, custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if cog:
            await cog.create_ticket(interaction, "support")
        else:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)

class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎯 Claim", style=discord.ButtonStyle.success, custom_id="ticket_claim")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Ticket claimato! (Funzionalità in sviluppo)", ephemeral=True)
    
    @discord.ui.button(label="🔒 Chiudi", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Ticket chiuso! (Funzionalità in sviluppo)", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
