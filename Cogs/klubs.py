import discord
from discord.ext import commands
import asyncio
import os

class Klubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.klubs = {}
        
        # Configurazione - modifica questi ID secondo le tue esigenze
        self.ALLOWED_ROLE_IDS = [1392128530438951084]  # VERIFIED_ROLE_ID di default
        self.KLUBS_CHANNEL_ID = 1411451850485403830  # PARTNERSHIP_CHANNEL_ID di default
        self.VOICE_CATEGORY_ID = None  # Sarà impostato automaticamente
        
    async def get_klubs_category(self, guild):
        """Crea o ottiene la categoria per i klub"""
        if self.VOICE_CATEGORY_ID:
            category = guild.get_channel(self.VOICE_CATEGORY_ID)
            if category:
                return category
        
        # Cerca una categoria esistente
        for category in guild.categories:
            if "klubs" in category.name.lower():
                self.VOICE_CATEGORY_ID = category.id
                return category
        
        # Crea una nuova categoria
        category = await guild.create_category("🎯 KLUBS", position=0)
        self.VOICE_CATEGORY_ID = category.id
        return category

    class Klub:
        def __init__(self, owner, voice_channel, text_channel, name):
            self.owner = owner
            self.voice_channel = voice_channel
            self.text_channel = text_channel
            self.name = name
            self.locked = False
            self.trusted_users = [owner]

    def has_allowed_role(self):
        async def predicate(ctx):
            user_roles = [role.id for role in ctx.author.roles]
            return any(role_id in user_roles for role_id in self.ALLOWED_ROLE_IDS)
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        """Inizializza il sistema Klubs quando il bot è pronto"""
        print("✅ Sistema Klubs caricato!")
        
        # Trova il canale klubs e invia il messaggio
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.KLUBS_CHANNEL_ID)
            if channel:
                # Pulisci i vecchi messaggi del bot
                async for message in channel.history(limit=10):
                    if message.author == self.bot.user:
                        await message.delete()
                
                await self.send_klubs_message(channel)
                break

    async def send_klubs_message(self, channel):
        """Crea il messaggio embed per i klubs"""
        embed = discord.Embed(
            title="🎯 EChat APP - Klubs System",
            description="Sistema di vocali privati",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="Cosa sono i Klubs?",
            value="I Klubs sono vocali privati dove decidi tu chi può entrare!",
            inline=False
        )
        
        embed.add_field(
            name="Permessi necessari",
            value="Clicca il pulsante qui sotto per vedere i ruoli autorizzati",
            inline=False
        )
        
        embed.add_field(
            name="Comandi disponibili:",
            value=(
                "`/klub create [nome]` - Crea un nuovo klub\n"
                "`/klub edit [nome]` - Modifica il nome\n"
                "`/klub lock` - Blocca l'accesso (solo trusted)\n"
                "`/klub unlock` - Sblocca l'accesso\n"
                "`/klub trust [@utente]` - Aggiungi utente trusted\n"
                "`/klub delete` - Elimina il klub"
            ),
            inline=False
        )
        
        # Crea i pulsanti
        view = discord.ui.View()
        
        # Pulsante per vedere i ruoli
        roles_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="📋 Visualizza Ruoli Autorizzati",
            custom_id="show_roles"
        )
        
        async def roles_callback(interaction):
            user_roles = [role.id for role in interaction.user.roles]
            has_allowed_role = any(role_id in user_roles for role_id in self.ALLOWED_ROLE_IDS)
            
            if has_allowed_role:
                roles_list = "\n".join([f"• <@&{role_id}>" for role_id in self.ALLOWED_ROLE_IDS])
                await interaction.response.send_message(
                    f"**Ruoli autorizzati a creare Klubs:**\n{roles_list}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Non hai i permessi per visualizzare questa informazione.",
                    ephemeral=True
                )
        
        roles_button.callback = roles_callback
        view.add_item(roles_button)
        
        await channel.send(embed=embed, view=view)

    @discord.app_commands.command(name="klub", description="Gestisci i tuoi Klubs")
    @discord.app_commands.describe(
        action="Azione da eseguire",
        name="Nome del klub",
        user="Utente da aggiungere come trusted"
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="create", value="create"),
        discord.app_commands.Choice(name="edit", value="edit"),
        discord.app_commands.Choice(name="lock", value="lock"),
        discord.app_commands.Choice(name="unlock", value="unlock"),
        discord.app_commands.Choice(name="trust", value="trust"),
        discord.app_commands.Choice(name="delete", value="delete")
    ])
    async def klub_command(self, interaction: discord.Interaction, 
                          action: discord.app_commands.Choice[str],
                          name: str = None,
                          user: discord.Member = None):
        
        # Verifica permessi per creare
        if action.value == "create":
            user_roles = [role.id for role in interaction.user.roles]
            if not any(role_id in user_roles for role_id in self.ALLOWED_ROLE_IDS):
                await interaction.response.send_message(
                    "❌ Non hai i permessi per creare un Klub!",
                    ephemeral=True
                )
                return
        
        await getattr(self, f"klub_{action.value}")(interaction, name, user)

    async def klub_create(self, interaction, name, user):
        """Crea un nuovo klub"""
        if not name:
            await interaction.response.send_message("❌ Devi specificare un nome!", ephemeral=True)
            return
        
        if interaction.user.id in self.klubs:
            await interaction.response.send_message(
                "❌ Hai già un klub attivo! Eliminalo prima di crearne uno nuovo.",
                ephemeral=True
            )
            return
        
        guild = interaction.guild
        category = await self.get_klubs_category(guild)
        
        # Crea canale vocale
        voice_channel = await guild.create_voice_channel(
            name=f"🔒 {name}",
            category=category,
            user_limit=10
        )
        
        # Crea canale testuale privato
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, 
                connect=True, 
                speak=True,
                send_messages=True
            ),
            self.bot.user: discord.PermissionOverwrite(
                view_channel=True, 
                manage_channels=True
            )
        }
        
        text_channel = await guild.create_text_channel(
            name=f"klub-{name.lower().replace(' ', '-')}",
            category=category,
            overwrites=overwrites
        )
        
        # Salva il klub
        self.klubs[interaction.user.id] = self.Klub(
            interaction.user, voice_channel, text_channel, name
        )
        
        embed = discord.Embed(
            title="🎉 Klub Creato!",
            description=f"**{name}** è stato creato con successo!",
            color=0x00ff00
        )
        embed.add_field(name="Canale Vocale", value=voice_channel.mention)
        embed.add_field(name="Canale Testuale", value=text_channel.mention)
        embed.add_field(
            name="Comandi", 
            value="Usa `/klub` per gestire il tuo klub", 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def klub_lock(self, interaction, name, user):
        """Blocca l'accesso al klub"""
        if interaction.user.id not in self.klubs:
            await interaction.response.send_message("❌ Non hai un klub attivo!", ephemeral=True)
            return
        
        klub = self.klubs[interaction.user.id]
        klub.locked = True
        
        # Aggiorna i permessi del canale vocale
        overwrites = klub.voice_channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(connect=False)
        
        for trusted_user in klub.trusted_users:
            overwrites[trusted_user] = discord.PermissionOverwrite(connect=True)
        
        await klub.voice_channel.edit(overwrites=overwrites)
        await interaction.response.send_message("🔒 Klub bloccato! Solo gli utenti trusted possono entrare.")

    async def klub_unlock(self, interaction, name, user):
        """Sblocca l'accesso al klub"""
        if interaction.user.id not in self.klubs:
            await interaction.response.send_message("❌ Non hai un klub attivo!", ephemeral=True)
            return
        
        klub = self.klubs[interaction.user.id]
        klub.locked = False
        
        # Ripristina permessi default
        overwrites = klub.voice_channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(connect=True)
        
        await klub.voice_channel.edit(overwrites=overwrites)
        await interaction.response.send_message("🔓 Klub sbloccato! Tutti possono entrare.")

    async def klub_trust(self, interaction, name, user):
        """Aggiungi un utente trusted"""
        if interaction.user.id not in self.klubs:
            await interaction.response.send_message("❌ Non hai un klub attivo!", ephemeral=True)
            return
        
        if not user:
            await interaction.response.send_message("❌ Devi specificare un utente!", ephemeral=True)
            return
        
        klub = self.klubs[interaction.user.id]
        
        if user not in klub.trusted_users:
            klub.trusted_users.append(user)
        
        # Aggiorna permessi
        overwrites = klub.voice_channel.overwrites
        overwrites[user] = discord.PermissionOverwrite(connect=True, view_channel=True)
        
        # Aggiorna anche il canale testuale
        text_overwrites = klub.text_channel.overwrites
        text_overwrites[user] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        
        await klub.voice_channel.edit(overwrites=overwrites)
        await klub.text_channel.edit(overwrites=text_overwrites)
        await interaction.response.send_message(f"✅ {user.mention} è ora un utente trusted!")

    async def klub_delete(self, interaction, name, user):
        """Elimina il klub"""
        if interaction.user.id not in self.klubs:
            await interaction.response.send_message("❌ Non hai un klub attivo!", ephemeral=True)
            return
        
        klub = self.klubs[interaction.user.id]
        
        # Elimina canali
        await klub.voice_channel.delete()
        await klub.text_channel.delete()
        
        # Rimuovi dal dizionario
        del self.klubs[interaction.user.id]
        
        await interaction.response.send_message("🗑️ Klub eliminato con successo!")

    async def klub_edit(self, interaction, name, user):
        """Modifica il nome del klub"""
        if interaction.user.id not in self.klubs:
            await interaction.response.send_message("❌ Non hai un klub attivo!", ephemeral=True)
            return
        
        if not name:
            await interaction.response.send_message("❌ Devi specificare un nuovo nome!", ephemeral=True)
            return
        
        klub = self.klubs[interaction.user.id]
        klub.name = name
        
        # Aggiorna nomi canali
        await klub.voice_channel.edit(name=f"🔒 {name}")
        await klub.text_channel.edit(name=f"klub-{name.lower().replace(' ', '-')}")
        
        await interaction.response.send_message(f"✏️ Nome del klub cambiato in **{name}**")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Pulisce i klub quando il proprietario esce"""
        if member.id in self.klubs:
            klub = self.klubs[member.id]
            
            # Se il proprietario esce dal canale vocale
            if after.channel != klub.voice_channel:
                # Attendi 5 secondi prima di controllare
                await asyncio.sleep(5)
                
                # Se il canale è vuoto, eliminalo
                if len(klub.voice_channel.members) == 0:
                    try:
                        await klub.voice_channel.delete()
                        await klub.text_channel.delete()
                    except:
                        pass  # Canali già eliminati
                    finally:
                        if member.id in self.klubs:
                            del self.klubs[member.id]

async def setup(bot):
    await bot.add_cog(Klubs(bot))
