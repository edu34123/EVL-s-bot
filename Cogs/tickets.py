import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from datetime import datetime

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Configurazione
        self.TICKET_CATEGORY_ITA = int(os.getenv('TICKET_CATEGORY_ITA', '1400000000000000000'))
        self.TICKET_CATEGORY_ENG = int(os.getenv('TICKET_CATEGORY_ENG', '1400000000000000001'))
        self.TICKET_LOG_CHANNEL = int(os.getenv('TICKET_LOG_CHANNEL', '1400000000000000002'))
        
        # Ruoli staff
        self.STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID', '1400000000000000003'))
        self.PARTNERSHIP_ROLE_ID = int(os.getenv('PARTNERSHIP_ROLE_ID', '1400000000000000004'))
        self.SUPPORT_ROLE_ID = int(os.getenv('SUPPORT_ROLE_ID', '1400000000000000005'))
        
        # Ruoli lingua
        self.ITA_ROLE_ID = int(os.getenv('ITA_ROLE_ID', '1402668379533348944'))
        self.ENG_ROLE_ID = int(os.getenv('ENG_ROLE_ID', '1402668928890568785'))
        
        # Dizionario per tenere traccia dei ticket aperti
        self.open_tickets = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Avvia il sistema ticket quando il bot è pronto"""
        print("✅ Sistema Ticket caricato!")
        # Aggiungi la view persistente per i pulsanti ticket
        self.bot.add_view(TicketCreationView())

    @app_commands.command(name="setup_tickets", description="Setup sistema ticket (Admin)")
    @app_commands.default_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup dei messaggi ticket per italiano e inglese"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Embed per ticket italiano
            embed_ita = discord.Embed(
                title="🎫 SISTEMA TICKET - ITALIANO 🇮🇹",
                color=0x00ff00,
                description="**Apri un ticket per richiedere assistenza o partnership!**"
            )
            
            embed_ita.add_field(
                name="📋 Tipi di Ticket Disponibili",
                value="""
**🤝 Partnership** - Per collaborazioni e partnership
**🛠️ Supporto** - Per assistenza e problemi tecnici

Clicca il pulsante corrispondente per aprire un ticket!
                """,
                inline=False
            )
            
            embed_ita.add_field(
                name="📜 Regole Ticket",
                value="""
• Non taggare lo staff, verranno automaticamente notificati
• Il ticket verrà chiuso dopo 24h di inattività
• Sii chiaro e conciso nella tua richiesta
• Rispetta lo staff e le sue decisioni
                """,
                inline=False
            )
            
            # Embed per ticket inglese
            embed_eng = discord.Embed(
                title="🎫 TICKET SYSTEM - ENGLISH 🇬🇧",
                color=0x0099ff,
                description="**Open a ticket to request assistance or partnership!**"
            )
            
            embed_eng.add_field(
                name="📋 Available Ticket Types",
                value="""
**🤝 Partnership** - For collaborations and partnerships
**🛠️ Support** - For assistance and technical issues

Click the corresponding button to open a ticket!
                """,
                inline=False
            )
            
            embed_eng.add_field(
                name="📜 Ticket Rules",
                value="""
• Don't ping staff, they will be automatically notified
• Ticket will be closed after 24h of inactivity
• Be clear and concise in your request
• Respect staff and their decisions
                """,
                inline=False
            )
            
            # Crea i pulsanti per entrambe le lingue
            view_ita = TicketCreationView()
            view_eng = TicketCreationView()
            
            # Invia i messaggi
            await interaction.channel.send(embed=embed_ita, view=view_ita)
            await interaction.channel.send(embed=embed_eng, view=view_eng)
            
            await interaction.followup.send("✅ Sistema ticket configurato correttamente!", ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Errore durante il setup: {e}", ephemeral=True)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        """Crea un nuovo ticket"""
        try:
            guild = interaction.guild
            member = interaction.user
            
            # Determina la categoria in base alla lingua
            if language == "ita":
                category_id = self.TICKET_CATEGORY_ITA
                ticket_name = f"ticket-{ticket_type}-{member.display_name}"
                staff_message = "Staff sarà con te a breve!"
            else:
                category_id = self.TICKET_CATEGORY_ENG
                ticket_name = f"ticket-{ticket_type}-{member.display_name}"
                staff_message = "Staff will be with you shortly!"
            
            category = guild.get_channel(category_id)
            if not category:
                await interaction.response.send_message("❌ Categoria ticket non trovata!", ephemeral=True)
                return
            
            # Crea il canale ticket
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
            
            # Aggiungi permessi per tutti i ruoli staff
            staff_role = guild.get_role(self.STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            
            # Crea il canale
            ticket_channel = await category.create_text_channel(
                name=ticket_name,
                overwrites=overwrites,
                topic=f"Ticket {ticket_type} - {member.display_name}"
            )
            
            # Salva informazioni del ticket
            self.open_tickets[ticket_channel.id] = {
                "owner": member.id,
                "type": ticket_type,
                "language": language,
                "claimed_by": None,
                "created_at": datetime.now()
            }
            
            # Determina il ruolo da taggare in base al tipo di ticket
            if ticket_type == "partnership":
                role_to_ping = guild.get_role(self.PARTNERSHIP_ROLE_ID)
                role_name = "Partnership"
            else:  # support
                role_to_ping = guild.get_role(self.SUPPORT_ROLE_ID)
                role_name = "Support"
            
            # Embed del ticket
            if language == "ita":
                embed = discord.Embed(
                    title=f"🎫 Ticket {role_name} - {member.display_name}",
                    color=0x00ff00,
                    description=f"**Ticket aperto da:** {member.mention}\n**Tipo:** {role_name}\n**Stato:** 🔓 In attesa di staff"
                )
                
                embed.add_field(
                    name="📜 Regole del Ticket",
                    value="""
• Non taggare lo staff, verranno automaticamente notificati
• Il ticket verrà chiuso dopo 24h di inattività
• Lo staff ti risponderà al più presto
                    """,
                    inline=False
                )
                
                embed.add_field(
                    name="🎯 Azioni Disponibili",
                    value="""
• **Claim** - Prendi in carico il ticket
• **Chiudi** - Chiudi il ticket
• **Aggiungi** - Aggiungi altro staff (solo dopo claim)
                    """,
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title=f"🎫 {role_name} Ticket - {member.display_name}",
                    color=0x0099ff,
                    description=f"**Ticket opened by:** {member.mention}\n**Type:** {role_name}\n**Status:** 🔓 Waiting for staff"
                )
                
                embed.add_field(
                    name="📜 Ticket Rules",
                    value="""
• Don't ping staff, they will be automatically notified
• Ticket will be closed after 24h of inactivity
• Staff will reply as soon as possible
                    """,
                    inline=False
                )
                
                embed.add_field(
                    name="🎯 Available Actions",
                    value="""
• **Claim** - Take over the ticket
• **Close** - Close the ticket
• **Add** - Add other staff (after claim only)
                    """,
                    inline=False
                )
            
            # Crea i pulsanti per il ticket
            view = TicketManagementView()
            
            # Messaggio iniziale
            ping_message = ""
            if role_to_ping:
                ping_message = f"{role_to_ping.mention} "
            
            if language == "ita":
                ping_message += f"Nuovo ticket {role_name} aperto da {member.mention}!"
            else:
                ping_message += f"New {role_name} ticket opened by {member.mention}!"
            
            await ticket_channel.send(ping_message, embed=embed, view=view)
            
            # Messaggio di conferma all'utente
            if language == "ita":
                await interaction.response.send_message(
                    f"✅ Ticket creato correttamente! Vai in {ticket_channel.mention}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"✅ Ticket created successfully! Go to {ticket_channel.mention}",
                    ephemeral=True
                )
            
            # Log del ticket
            await self.log_ticket_creation(ticket_channel, member, ticket_type, language)
            
        except Exception as e:
            if language == "ita":
                await interaction.response.send_message(f"❌ Errore nella creazione del ticket: {e}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Error creating ticket: {e}", ephemeral=True)

    async def claim_ticket(self, interaction: discord.Interaction):
        """Claim di un ticket da parte dello staff"""
        try:
            channel = interaction.channel
            ticket_info = self.open_tickets.get(channel.id)
            
            if not ticket_info:
                await interaction.response.send_message("❌ Questo canale non è un ticket valido!", ephemeral=True)
                return
            
            if ticket_info["claimed_by"]:
                if ticket_info["language"] == "ita":
                    await interaction.response.send_message("❌ Questo ticket è già stato claimato!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ This ticket is already claimed!", ephemeral=True)
                return
            
            # Aggiorna i permessi - solo lo staff che ha claimato può scrivere
            overwrites = channel.overwrites
            staff_role = interaction.guild.get_role(self.STAFF_ROLE_ID)
            
            # Rimuovi permessi di scrittura a tutti i ruoli staff
            if staff_role in overwrites:
                overwrites[staff_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,  # Non può più scrivere
                    read_message_history=True
                )
            
            # Da permessi di scrittura solo allo staff che ha claimato
            overwrites[interaction.user] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
            
            await channel.edit(overwrites=overwrites)
            
            # Aggiorna informazioni del ticket
            ticket_info["claimed_by"] = interaction.user.id
            self.open_tickets[channel.id] = ticket_info
            
            # Messaggio di conferma
            if ticket_info["language"] == "ita":
                embed = discord.Embed(
                    description=f"✅ **Ticket claimato da {interaction.user.mention}**\nOra solo lo staff claimato può scrivere in questo ticket.",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    description=f"✅ **Ticket claimed by {interaction.user.mention}**\nNow only the claimed staff can write in this ticket.",
                    color=0x00ff00
                )
            
            await interaction.response.send_message(embed=embed)
            
            # Aggiorna la view dei pulsanti
            view = TicketManagementView()
            await interaction.message.edit(view=view)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore durante il claim: {e}", ephemeral=True)

    async def close_ticket(self, interaction: discord.Interaction):
        """Chiude un ticket"""
        try:
            channel = interaction.channel
            ticket_info = self.open_tickets.get(channel.id)
            
            if not ticket_info:
                await interaction.response.send_message("❌ Questo canale non è un ticket valido!", ephemeral=True)
                return
            
            # Log della chiusura
            await self.log_ticket_closing(channel, interaction.user, ticket_info)
            
            # Messaggio di chiusura
            if ticket_info["language"] == "ita":
                embed = discord.Embed(
                    description="🔒 **Ticket chiuso**\nIl ticket verrà eliminato in 10 secondi...",
                    color=0xff0000
                )
            else:
                embed = discord.Embed(
                    description="🔒 **Ticket closed**\nThe ticket will be deleted in 10 seconds...",
                    color=0xff0000
                )
            
            await interaction.response.send_message(embed=embed)
            
            # Attesa e eliminazione
            await asyncio.sleep(10)
            await channel.delete()
            
            # Rimuovi dalle ticket aperte
            if channel.id in self.open_tickets:
                del self.open_tickets[channel.id]
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore durante la chiusura: {e}", ephemeral=True)

    async def add_staff_to_ticket(self, interaction: discord.Interaction, staff_member: discord.Member):
        """Aggiunge staff al ticket"""
        try:
            channel = interaction.channel
            ticket_info = self.open_tickets.get(channel.id)
            
            if not ticket_info:
                await interaction.response.send_message("❌ Questo canale non è un ticket valido!", ephemeral=True)
                return
            
            if ticket_info["claimed_by"] != interaction.user.id:
                if ticket_info["language"] == "ita":
                    await interaction.response.send_message("❌ Solo lo staff che ha claimato il ticket può aggiungere altri staff!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Only the staff who claimed the ticket can add other staff!", ephemeral=True)
                return
            
            # Verifica che sia staff
            staff_role = interaction.guild.get_role(self.STAFF_ROLE_ID)
            if staff_role not in staff_member.roles:
                if ticket_info["language"] == "ita":
                    await interaction.response.send_message("❌ Questo utente non è staff!", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ This user is not staff!", ephemeral=True)
                return
            
            # Aggiungi permessi
            overwrites = channel.overwrites
            overwrites[staff_member] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
            
            await channel.edit(overwrites=overwrites)
            
            if ticket_info["language"] == "ita":
                embed = discord.Embed(
                    description=f"✅ **{staff_member.mention} aggiunto al ticket**",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    description=f"✅ **{staff_member.mention} added to the ticket**",
                    color=0x00ff00
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore durante l'aggiunta: {e}", ephemeral=True)

    async def log_ticket_creation(self, channel, member, ticket_type, language):
        """Log della creazione del ticket"""
        log_channel = self.bot.get_channel(self.TICKET_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="📝 NUOVO TICKET APERTO",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="👤 Utente", value=f"{member.mention} ({member.id})", inline=True)
            embed.add_field(name="🎯 Tipo", value=ticket_type.capitalize(), inline=True)
            embed.add_field(name="🌍 Lingua", value="Italiano" if language == "ita" else "English", inline=True)
            embed.add_field(name="📁 Canale", value=channel.mention, inline=True)
            
            await log_channel.send(embed=embed)

    async def log_ticket_closing(self, channel, closer, ticket_info):
        """Log della chiusura del ticket"""
        log_channel = self.bot.get_channel(self.TICKET_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🔒 TICKET CHIUSO",
                color=0xff0000,
                timestamp=datetime.now()
            )
            
            owner = self.bot.get_user(ticket_info["owner"])
            claimed_by = self.bot.get_user(ticket_info["claimed_by"]) if ticket_info["claimed_by"] else None
            
            embed.add_field(name="👤 Creatore", value=f"{owner.mention if owner else 'N/A'} ({ticket_info['owner']})", inline=True)
            embed.add_field(name="🎯 Tipo", value=ticket_info["type"].capitalize(), inline=True)
            embed.add_field(name="👮 Claimed da", value=f"{claimed_by.mention if claimed_by else 'Nessuno'}", inline=True)
            embed.add_field(name="👮 Chiuso da", value=closer.mention, inline=True)
            embed.add_field(name="⏰ Durata", value=f"{(datetime.now() - ticket_info['created_at']).seconds // 60} minuti", inline=True)
            
            await log_channel.send(embed=embed)

class TicketCreationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🤝 Partnership", style=discord.ButtonStyle.primary, custom_id="ticket_partnership")
    async def partnership_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
            return
        
        # Determina la lingua in base ai ruoli dell'utente
        ita_role = interaction.guild.get_role(cog.ITA_ROLE_ID)
        eng_role = interaction.guild.get_role(cog.ENG_ROLE_ID)
        
        language = "ita" if ita_role and ita_role in interaction.user.roles else "eng"
        await cog.create_ticket(interaction, "partnership", language)
    
    @discord.ui.button(label="🛠️ Supporto", style=discord.ButtonStyle.secondary, custom_id="ticket_support")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
            return
        
        # Determina la lingua in base ai ruoli dell'utente
        ita_role = interaction.guild.get_role(cog.ITA_ROLE_ID)
        eng_role = interaction.guild.get_role(cog.ENG_ROLE_ID)
        
        language = "ita" if ita_role and ita_role in interaction.user.roles else "eng"
        await cog.create_ticket(interaction, "support", language)

class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎯 Claim", style=discord.ButtonStyle.success, custom_id="ticket_claim")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
            return
        await cog.claim_ticket(interaction)
    
    @discord.ui.button(label="🔒 Chiudi", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
            return
        await cog.close_ticket(interaction)
    
    @discord.ui.button(label="👥 Aggiungi Staff", style=discord.ButtonStyle.primary, custom_id="ticket_add_staff")
    async def add_staff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog('TicketSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
            return
        
        # Crea una modal per selezionare lo staff
        await interaction.response.send_modal(AddStaffModal())

class AddStaffModal(discord.ui.Modal, title="Aggiungi Staff al Ticket"):
    staff_id = discord.ui.TextInput(
        label="ID Staff Member",
        placeholder="Inserisci l'ID dello staff da aggiungere",
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog('TicketSystem')
        if not cog:
            await interaction.response.send_message("❌ Sistema ticket non disponibile", ephemeral=True)
            return
        
        try:
            staff_member = await interaction.guild.fetch_member(int(self.staff_id.value))
            await cog.add_staff_to_ticket(interaction, staff_member)
        except ValueError:
            await interaction.response.send_message("❌ ID non valido!", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ Utente non trovato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
