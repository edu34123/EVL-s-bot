import discord
from discord.ext import commands, tasks
import aiosqlite
from datetime import datetime
import asyncio

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.LEVEL_CHANNEL_ID = 1392483787384029294  # Imposta con il canale desiderato
        self.leaderboard_messages = {}  # {guild_id: message_id}
        self.update_leaderboard.start()
        
        # Inizializza il database
        self.bot.loop.create_task(self.init_db())

    async def init_db(self):
        """Inizializza il database"""
        async with aiosqlite.connect('database.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS levels (
                    user_id INTEGER,
                    guild_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    messages INTEGER DEFAULT 0,
                    last_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            await db.commit()

    def cog_unload(self):
        """Ferma il task quando il cog viene scaricato"""
        self.update_leaderboard.cancel()

    @tasks.loop(minutes=30)
    async def update_leaderboard(self):
        """Task automatico per aggiornare la leaderboard"""
        if self.LEVEL_CHANNEL_ID == 0:
            return
            
        try:
            for guild in self.bot.guilds:
                channel = guild.get_channel(self.LEVEL_CHANNEL_ID)
                if channel:
                    await self.send_or_update_leaderboard(channel, guild)
                    await asyncio.sleep(1)  # Delay tra un aggiornamento e l'altro
        except Exception as e:
            print(f"❌ Errore aggiornamento leaderboard automatico: {e}")

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        """Aspetta che il bot sia pronto prima di iniziare il task"""
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Gestisce l'XP quando viene inviato un messaggio"""
        if message.author.bot or not message.guild:
            return
        
        # Aggiorna l'XP dell'utente
        await self.update_user_xp(message.author, message.guild)

    async def update_user_xp(self, user, guild):
        """Aggiorna l'XP di un utente"""
        async with aiosqlite.connect('database.db') as db:
            # Ottieni i dati attuali dell'utente
            cursor = await db.execute(
                'SELECT xp, level, messages FROM levels WHERE user_id = ? AND guild_id = ?',
                (user.id, guild.id)
            )
            result = await cursor.fetchone()
            
            if result:
                xp, level, messages = result
                new_xp = xp + 5  # +5 XP per messaggio
                new_messages = messages + 1
            else:
                new_xp = 5
                level = 1
                new_messages = 1
            
            # Calcola il nuovo livello
            new_level = self.calculate_level(new_xp)
            
            # Aggiorna il database
            await db.execute(
                '''INSERT OR REPLACE INTO levels (user_id, guild_id, xp, level, messages, last_message)
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                (user.id, guild.id, new_xp, new_level, new_messages)
            )
            await db.commit()
            
            # Controlla se l'utente è salito di livello
            if new_level > level:
                await self.handle_level_up(user, guild, new_level)

    def calculate_level(self, xp):
        """Calcola il livello basato sull'XP (formula: level = sqrt(xp) / 5)"""
        return max(1, int((xp ** 0.5) / 5))

    def calculate_xp_for_level(self, level):
        """Calcola l'XP necessario per un determinato livello"""
        return (level * 5) ** 2

    async def handle_level_up(self, user, guild, new_level):
        """Gestisce il livello raggiunto"""
        # Puoi aggiungere notifiche o ricompense qui
        print(f"🎉 {user.display_name} è salito al livello {new_level} in {guild.name}")

    @discord.app_commands.command(name="level", description="Mostra il tuo livello e XP")
    @discord.app_commands.describe(member="L'utente di cui vedere il livello (opzionale)")
    async def check_level(self, interaction: discord.Interaction, member: discord.Member = None):
        """Mostra il livello e l'XP dell'utente"""
        if member is None:
            member = interaction.user
        
        await interaction.response.defer()
        
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute(
                'SELECT xp, level, messages FROM levels WHERE user_id = ? AND guild_id = ?',
                (member.id, interaction.guild.id)
            )
            result = await cursor.fetchone()
            
            if result:
                xp, level, messages = result
                xp_next_level = self.calculate_xp_for_level(level + 1)
                xp_current_level = self.calculate_xp_for_level(level)
                xp_progress = xp - xp_current_level
                xp_needed = xp_next_level - xp_current_level
                
                # Calcola la percentuale di progresso
                progress_percentage = (xp_progress / xp_needed) * 100
                
                # Crea la barra di progresso
                progress_bar = self.create_progress_bar(progress_percentage)
                
                embed = discord.Embed(
                    title=f"📊 Livello di {member.display_name}",
                    color=0x00ff00
                )
                embed.add_field(
                    name="Statistiche",
                    value=(
                        f"**Livello:** {level}\n"
                        f"**XP:** {xp:,}/{xp_next_level:,}\n"
                        f"**Progresso:** {progress_percentage:.1f}%\n"
                        f"**Messaggi:** {messages:,}\n"
                        f"**Barra Progresso:**\n{progress_bar}"
                    ),
                    inline=False
                )
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"{member.mention} non ha ancora accumulato XP in questo server!")

    def create_progress_bar(self, percentage, length=20):
        """Crea una barra di progresso visuale"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"`[{bar}]`"

    @discord.app_commands.command(name="leaderboard", description="Mostra la classifica dei livelli del server")
    async def show_leaderboard(self, interaction: discord.Interaction):
        """Mostra la leaderboard del server"""
        await interaction.response.defer()
        
        embed = await self.create_leaderboard_embed(interaction.guild)
        await interaction.followup.send(embed=embed)

    async def send_or_update_leaderboard(self, channel, guild):
        """Invia o aggiorna la leaderboard nel canale specifico per ogni guild"""
        try:
            embed = await self.create_leaderboard_embed(guild)
            
            # Ottieni il message_id per questa guild
            message_id = self.leaderboard_messages.get(guild.id)
            
            # Cerca il messaggio esistente del bot
            if message_id:
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(embed=embed)
                    print(f"✅ Leaderboard aggiornata per {guild.name}")
                    return
                except discord.NotFound:
                    self.leaderboard_messages.pop(guild.id, None)
                except discord.Forbidden:
                    print(f"❌ Permessi insufficienti per modificare il messaggio in {guild.name}")
                    return
            
            # Se non esiste, cerca nella cronologia
            async for message in channel.history(limit=20):
                if message.author == self.bot.user and message.embeds:
                    for embed_msg in message.embeds:
                        if embed_msg.title and "Classifica Livelli" in embed_msg.title:
                            self.leaderboard_messages[guild.id] = message.id
                            await message.edit(embed=embed)
                            print(f"✅ Leaderboard aggiornata (messaggio esistente) per {guild.name}")
                            return
            
            # Crea un nuovo messaggio
            message = await channel.send(embed=embed)
            self.leaderboard_messages[guild.id] = message.id
            print(f"✅ Leaderboard creata per {guild.name}")
            
        except discord.Forbidden:
            print(f"❌ Permessi insufficienti per inviare/modificare messaggi in {guild.name}")
        except Exception as e:
            print(f"❌ Errore invio/aggiornamento leaderboard per {guild.name}: {e}")

    async def create_leaderboard_embed(self, guild):
        """Crea l'embed della leaderboard"""
        try:
            async with aiosqlite.connect('database.db') as db:
                cursor = await db.execute(
                    '''SELECT user_id, xp, level, messages 
                       FROM levels 
                       WHERE guild_id = ? 
                       ORDER BY xp DESC 
                       LIMIT 15''',
                    (guild.id,)
                )
                results = await cursor.fetchall()
                
                if not results:
                    embed = discord.Embed(
                        title="🏆 Classifica Livelli",
                        description="*Nessun dato disponibile ancora...*",
                        color=0xffd700
                    )
                    embed.set_footer(text="La classifica si aggiorna automaticamente ogni 30 minuti")
                    return embed
                
                embed = discord.Embed(
                    title="🏆 Classifica Livelli - Top 15",
                    description="Classifica degli utenti più attivi del server",
                    color=0xffd700,
                    timestamp=datetime.now()
                )
                
                leaderboard_text = ""
                for i, (user_id, xp, level, messages) in enumerate(results, 1):
                    user = guild.get_member(user_id)
                    username = user.display_name if user else f"❓ Utente Sconosciuto ({user_id})"
                    
                    # Emoji per le prime posizioni
                    if i == 1: 
                        medal = "🥇"
                    elif i == 2: 
                        medal = "🥈" 
                    elif i == 3: 
                        medal = "🥉"
                    else: 
                        medal = f"**#{i}**"
                    
                    leaderboard_text += (
                        f"{medal} **{username}**\n"
                        f"└ 📊 Livello **{level}** | ⭐ **{xp:,}** XP | 💬 **{messages}** messaggi\n\n"
                    )
                
                embed.description = leaderboard_text
                
                # Aggiungi statistiche generali
                total_users = len(results)
                total_xp = sum(xp for _, xp, _, _ in results)
                avg_level = sum(level for _, _, level, _ in results) / total_users if total_users > 0 else 0
                
                # Ottieni il totale degli utenti nel database
                cursor = await db.execute(
                    'SELECT COUNT(*) FROM levels WHERE guild_id = ?',
                    (guild.id,)
                )
                total_db_users = (await cursor.fetchone())[0]
                
                embed.add_field(
                    name="📈 Statistiche Server",
                    value=(
                        f"• **Utenti in classifica:** {total_users}\n"
                        f"• **Utenti totali nel database:** {total_db_users}\n"
                        f"• **XP totale:** {total_xp:,}\n"
                        f"• **Livello medio:** {avg_level:.1f}\n"
                        f"• **Ultimo aggiornamento:** <t:{int(datetime.now().timestamp())}:R>"
                    ),
                    inline=False
                )
                
                embed.set_footer(
                    text="Classifica aggiornata automaticamente ogni 30 minuti • Usa /level per vedere il tuo livello"
                )
                
                return embed
                
        except Exception as e:
            print(f"❌ Errore creazione embed leaderboard per {guild.name}: {e}")
            embed = discord.Embed(
                title="❌ Errore Classifica",
                description="Si è verificato un errore nel caricare la classifica.",
                color=0xff0000
            )
            return embed

    @discord.app_commands.command(name="set_level_channel", description="Imposta il canale per la leaderboard automatica")
    @discord.app_commands.describe(channel="Il canale dove mostrare la leaderboard")
    @discord.app_commands.default_permissions(administrator=True)
    async def set_level_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Imposta il canale per la leaderboard automatica"""
        await interaction.response.defer()
        
        self.LEVEL_CHANNEL_ID = channel.id
        
        # Salva il canale nel database
        async with aiosqlite.connect('database.db') as db:
            await db.execute(
                '''CREATE TABLE IF NOT EXISTS bot_config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )'''
            )
            await db.execute(
                'INSERT OR REPLACE INTO bot_config (key, value) VALUES (?, ?)',
                ('level_channel_id', str(channel.id))
            )
            await db.commit()
        
        await interaction.followup.send(f"✅ Canale leaderboard impostato su {channel.mention}")
        
        # Aggiorna immediatamente la leaderboard
        await self.send_or_update_leaderboard(channel, interaction.guild)

    @discord.app_commands.command(name="force_update", description="Forza l'aggiornamento della leaderboard")
    @discord.app_commands.default_permissions(administrator=True)
    async def force_update_leaderboard(self, interaction: discord.Interaction):
        """Forza l'aggiornamento della leaderboard"""
        await interaction.response.defer()
        
        if self.LEVEL_CHANNEL_ID == 0:
            await interaction.followup.send("❌ Nessun canale leaderboard impostato! Usa `/set_level_channel`")
            return
            
        channel = interaction.guild.get_channel(self.LEVEL_CHANNEL_ID)
        if channel:
            await self.send_or_update_leaderboard(channel, interaction.guild)
            await interaction.followup.send("✅ Leaderboard aggiornata manualmente!")
        else:
            await interaction.followup.send("❌ Canale leaderboard non trovato!")

    @discord.app_commands.command(name="user_stats", description="Mostra statistiche dettagliate di un utente")
    @discord.app_commands.describe(member="L'utente di cui vedere le statistiche")
    async def user_stats(self, interaction: discord.Interaction, member: discord.Member = None):
        """Mostra statistiche dettagliate di un utente"""
        if member is None:
            member = interaction.user
            
        await interaction.response.defer()
        
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute(
                '''SELECT xp, level, messages, last_message 
                   FROM levels 
                   WHERE user_id = ? AND guild_id = ?''',
                (member.id, interaction.guild.id)
            )
            result = await cursor.fetchone()
            
            if result:
                xp, level, messages, last_message = result
                
                # Calcola la posizione in classifica
                cursor = await db.execute(
                    '''SELECT COUNT(*) FROM levels 
                       WHERE guild_id = ? AND xp > ?''',
                    (interaction.guild.id, xp)
                )
                rank = (await cursor.fetchone())[0] + 1
                
                embed = discord.Embed(
                    title=f"📈 Statistiche di {member.display_name}",
                    color=member.color
                )
                
                embed.add_field(name="🏆 Posizione", value=f"#{rank}", inline=True)
                embed.add_field(name="📊 Livello", value=level, inline=True)
                embed.add_field(name="⭐ XP Totale", value=f"{xp:,}", inline=True)
                embed.add_field(name="💬 Messaggi", value=f"{messages:,}", inline=True)
                
                xp_next_level = self.calculate_xp_for_level(level + 1)
                xp_current_level = self.calculate_xp_for_level(level)
                xp_needed = xp_next_level - xp_current_level
                xp_progress = xp - xp_current_level
                progress_percentage = (xp_progress / xp_needed) * 100
                
                embed.add_field(
                    name="🎯 Progresso al prossimo livello",
                    value=f"{xp_progress:,}/{xp_needed:,} XP ({progress_percentage:.1f}%)",
                    inline=False
                )
                
                if last_message:
                    embed.add_field(
                        name="🕒 Ultimo messaggio",
                        value=f"<t:{int(datetime.fromisoformat(last_message).timestamp())}:R>",
                        inline=False
                    )
                
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"{member.mention} non ha ancora accumulato XP in questo server!")

    @discord.app_commands.command(name="rank", description="Mostra la tua posizione in classifica")
    @discord.app_commands.describe(member="L'utente di cui vedere la posizione")
    async def rank_command(self, interaction: discord.Interaction, member: discord.Member = None):
        """Mostra la posizione in classifica di un utente"""
        if member is None:
            member = interaction.user
            
        await interaction.response.defer()
        
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute(
                'SELECT xp, level, messages FROM levels WHERE user_id = ? AND guild_id = ?',
                (member.id, interaction.guild.id)
            )
            result = await cursor.fetchone()
            
            if result:
                xp, level, messages = result
                
                # Calcola la posizione in classifica
                cursor = await db.execute(
                    'SELECT COUNT(*) FROM levels WHERE guild_id = ? AND xp > ?',
                    (interaction.guild.id, xp)
                )
                rank = (await cursor.fetchone())[0] + 1
                
                # Calcola quanti utenti ci sono in classifica totale
                cursor = await db.execute(
                    'SELECT COUNT(*) FROM levels WHERE guild_id = ?',
                    (interaction.guild.id,)
                )
                total_users = (await cursor.fetchone())[0]
                
                embed = discord.Embed(
                    title=f"🏆 Posizione di {member.display_name}",
                    color=0x00ff00
                )
                
                embed.add_field(name="📊 Posizione", value=f"**#{rank}** su **{total_users}** utenti", inline=False)
                embed.add_field(name="⭐ XP", value=f"{xp:,}", inline=True)
                embed.add_field(name="🎯 Livello", value=level, inline=True)
                embed.add_field(name="💬 Messaggi", value=f"{messages:,}", inline=True)
                
                # Calcola la percentuale
                if total_users > 0:
                    percentile = ((total_users - rank) / total_users) * 100
                    embed.add_field(
                        name="📈 Percentile",
                        value=f"Sei nel top **{percentile:.1f}%** degli utenti!",
                        inline=False
                    )
                
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"{member.mention} non ha ancora accumulato XP in questo server!")

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
