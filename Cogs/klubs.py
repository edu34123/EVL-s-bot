import discord
from discord.ext import commands
import asyncio
import os

class Klubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.klubs = {}
        
        # Configurazione corretta
        self.ALLOWED_ROLE_IDS = [int(role_id.strip()) for role_id in os.getenv('KLUBS_ALLOWED_ROLES', '1402733312799412244,1311367694716633159,1407081522896572508,1394357096295956580').split(',')]
        self.KLUBS_CHANNEL_ID = int(os.getenv('KLUBS_CHANNEL_ID', '1402978154284453908'))
        
        print(f"✅ Configurazione Klubs caricata:")
        print(f"   - Ruoli autorizzati: {self.ALLOWED_ROLE_IDS}")
        print(f"   - Canale klubs: {self.KLUBS_CHANNEL_ID}")

    async def get_klubs_category(self, guild):
        """Crea o ottiene la categoria per i klub"""
        # Cerca una categoria esistente chiamata "Klubs"
        for category in guild.categories:
            if "klub" in category.name.lower():
                return category
        
        # Crea una nuova categoria
        category = await guild.create_category("🎯 KLUBS", position=0)
        return category

    class Klub:
        def __init__(self, owner, voice_channel, text_channel, name):
            self.owner = owner
            self.voice_channel = voice_channel
            self.text_channel = text_channel
            self.name = name
            self.locked = False
            self.trusted_users = [owner]

    @commands.Cog.listener()
    async def on_ready(self):
        """Inizializza il sistema Klubs quando il bot è pronto"""
        print("✅ Sistema Klubs caricato!")
        await asyncio.sleep(3)
        await self.setup_klubs_channel()

    async def setup_klubs_channel(self):
        """Configura il canale klubs"""
        for guild in self.bot.guilds:
            channel = guild.get_channel(self.KLUBS_CHANNEL_ID)
            if channel:
                try:
                    # Pulisci i vecchi messaggi del bot
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()
                    
                    await asyncio.sleep(1)
                    await self.send_klubs_message(channel)
                    print(f"✅ Messaggio klubs inviato in #{channel.name}")
                except Exception as e:
                    print(f"❌ Errore configurazione canale klubs: {e}")

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
            name="Comandi disponibili (prefisso >):",
            value=(
                "`>klub create [nome]` - Crea un nuovo klub\n"
                "`>klub edit [nome]` - Modifica il nome\n"
                "`>klub lock` - Blocca l'accesso (solo trusted)\n"
                "`>klub unlock` - Sblocca l'accesso\n"
                "`>klub trust [@utente]` - Aggiungi utente trusted\n"
                "`>klub delete` - Elimina il klub"
            ),
            inline=False
        )
        
        # Crea i pulsanti
        view = discord.ui.View(timeout=None)
        
        # Pulsante per vedere i ruoli autorizzati
        roles_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="👥 Mostra Ruoli Autorizzati",
            custom_id="show_roles"
        )
        
        async def roles_callback(interaction):
            # Mostra i ruoli autorizzati
            roles_list = ""
            for role_id in self.ALLOWED_ROLE_IDS:
                role = interaction.guild.get_role(role_id)
                if role:
                    roles_list += f"• {role.mention}\n"
                else:
                    roles_list += f"• <@&{role_id}> (ruolo non trovato)\n"
            
            embed = discord.Embed(
                title="👥 Ruoli Autorizzati per Klubs",
                description=roles_list,
                color=0x0099ff
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        roles_button.callback = roles_callback
        view.add_item(roles_button)
        
        # Pulsante per refresh
        refresh_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🔄 Aggiorna Messaggio",
            custom_id="refresh_klubs"
        )
        
        async def refresh_callback(interaction):
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Solo gli admin possono aggiornare il messaggio!", ephemeral=True)
                return
                
            await interaction.response.defer()
            await self.send_klubs_message(channel)
            await interaction.followup.send("✅ Messaggio aggiornato!", ephemeral=True)
        
        refresh_button.callback = refresh_callback
        view.add_item(refresh_button)
        
        await channel.send(embed=embed, view=view)

    def has_allowed_role(self):
        async def predicate(ctx):
            user_roles = [role.id for role in ctx.author.roles]
            return any(role_id in user_roles for role_id in self.ALLOWED_ROLE_IDS)
        return commands.check(predicate)

    @commands.command(name='klub_setup')
    @commands.has_permissions(administrator=True)
    async def klub_setup(self, ctx, channel: discord.TextChannel = None):
        """Configura il canale per i Klubs (solo admin)"""
        if channel is None:
            channel = ctx.channel
        
        self.KLUBS_CHANNEL_ID = channel.id
        await ctx.send(f"✅ Canale klubs impostato su {channel.mention}")
        await self.setup_klubs_channel()

    @commands.command(name='klub')
    async def klub_command(self, ctx, action: str = None, *, args: str = None):
        """Gestisci i tuoi Klubs"""
        if action is None:
            embed = discord.Embed(
                title="🎯 Comandi Klubs",
                description="Usa `>klub [azione]` per gestire i tuoi klub",
                color=0x00ff00
            )
            embed.add_field(
                name="Azioni disponibili:",
                value=(
                    "`create [nome]` - Crea un nuovo klub\n"
                    "`edit [nome]` - Modifica il nome\n"
                    "`lock` - Blocca l'accesso (solo trusted)\n"
                    "`unlock` - Sblocca l'accesso\n"
                    "`trust [@utente]` - Aggiungi utente trusted\n"
                    "`delete` - Elimina il klub"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return

        # Gestisci le diverse azioni
        action = action.lower()
        
        if action == "create":
            await self.klub_create(ctx, args)
        elif action == "edit":
            await self.klub_edit(ctx, args)
        elif action == "lock":
            await self.klub_lock(ctx)
        elif action == "unlock":
            await self.klub_unlock(ctx)
        elif action == "trust":
            await self.klub_trust(ctx, args)
        elif action == "delete":
            await self.klub_delete(ctx)
        else:
            await ctx.send("❌ Azione non riconosciuta! Usa `>klub` per vedere i comandi disponibili.")

    @klub_command.error
    async def klub_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Non hai i permessi per usare questo comando!")

    async def klub_create(self, ctx, name):
        """Crea un nuovo klub"""
        if not name:
            await ctx.send("❌ Devi specificare un nome! Es: `>klub create NomeKlub`")
            return
        
        # Verifica permessi
        user_roles = [role.id for role in ctx.author.roles]
        if not any(role_id in user_roles for role_id in self.ALLOWED_ROLE_IDS):
            await ctx.send("❌ Non hai i permessi per creare un Klub!")
            return
        
        if ctx.author.id in self.klubs:
            await ctx.send("❌ Hai già un klub attivo! Eliminalo prima di crearne uno nuovo.")
            return
        
        guild = ctx.guild
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
            ctx.author: discord.PermissionOverwrite(
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
        self.klubs[ctx.author.id] = self.Klub(
            ctx.author, voice_channel, text_channel, name
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
            value="Usa `>klub` per gestire il tuo klub", 
            inline=False
        )
        
        await ctx.send(embed=embed)

    async def klub_lock(self, ctx):
        """Blocca l'accesso al klub"""
        if ctx.author.id not in self.klubs:
            await ctx.send("❌ Non hai un klub attivo!")
            return
        
        klub = self.klubs[ctx.author.id]
        klub.locked = True
        
        # Aggiorna i permessi del canale vocale
        overwrites = klub.voice_channel.overwrites
        overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(connect=False)
        
        for trusted_user in klub.trusted_users:
            overwrites[trusted_user] = discord.PermissionOverwrite(connect=True)
        
        await klub.voice_channel.edit(overwrites=overwrites)
        await ctx.send("🔒 Klub bloccato! Solo gli utenti trusted possono entrare.")

    async def klub_unlock(self, ctx):
        """Sblocca l'accesso al klub"""
        if ctx.author.id not in self.klubs:
            await ctx.send("❌ Non hai un klub attivo!")
            return
        
        klub = self.klubs[ctx.author.id]
        klub.locked = False
        
        # Ripristina permessi default
        overwrites = klub.voice_channel.overwrites
        overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(connect=True)
        
        await klub.voice_channel.edit(overwrites=overwrites)
        await ctx.send("🔓 Klub sbloccato! Tutti possono entrare.")

    async def klub_trust(self, ctx, user_mention):
        """Aggiungi un utente trusted"""
        if ctx.author.id not in self.klubs:
            await ctx.send("❌ Non hai un klub attivo!")
            return
        
        if not user_mention:
            await ctx.send("❌ Devi specificare un utente! Es: `>klub trust @utente`")
            return
        
        # Estrai l'ID utente dalla menzione
        try:
            user_id = int(user_mention.replace('<@', '').replace('>', '').replace('!', ''))
            user = ctx.guild.get_member(user_id)
            
            if not user:
                await ctx.send("❌ Utente non trovato!")
                return
        except:
            await ctx.send("❌ Formato non valido! Usa: `>klub trust @utente`")
            return
        
        klub = self.klubs[ctx.author.id]
        
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
        await ctx.send(f"✅ {user.mention} è ora un utente trusted!")

    async def klub_delete(self, ctx):
        """Elimina il klub"""
        if ctx.author.id not in self.klubs:
            await ctx.send("❌ Non hai un klub attivo!")
            return
        
        klub = self.klubs[ctx.author.id]
        
        # Elimina canali
        try:
            await klub.voice_channel.delete()
            await klub.text_channel.delete()
        except:
            pass  # Canali già eliminati
        
        # Rimuovi dal dizionario
        if ctx.author.id in self.klubs:
            del self.klubs[ctx.author.id]
        
        await ctx.send("🗑️ Klub eliminato con successo!")

    async def klub_edit(self, ctx, new_name):
        """Modifica il nome del klub"""
        if ctx.author.id not in self.klubs:
            await ctx.send("❌ Non hai un klub attivo!")
            return
        
        if not new_name:
            await ctx.send("❌ Devi specificare un nuovo nome! Es: `>klub edit NuovoNome`")
            return
        
        klub = self.klubs[ctx.author.id]
        old_name = klub.name
        klub.name = new_name
        
        # Aggiorna nomi canali
        await klub.voice_channel.edit(name=f"🔒 {new_name}")
        await klub.text_channel.edit(name=f"klub-{new_name.lower().replace(' ', '-')}")
        
        await ctx.send(f"✏️ Nome del klub cambiato da **{old_name}** a **{new_name}**")

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
