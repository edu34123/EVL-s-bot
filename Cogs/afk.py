import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiosqlite
import asyncio
from datetime import datetime, timedelta

class AFKSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def init_db(self):
        """Inizializza le tabelle AFK nel database"""
        async with aiosqlite.connect('database.db') as db:
            # Tabella per sessioni AFK attive
            await db.execute('''
                CREATE TABLE IF NOT EXISTS afk_sessions (
                    user_id INTEGER,
                    guild_id INTEGER,
                    reason TEXT,
                    start_time TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            # Tabella per statistiche AFK giornaliere
            await db.execute('''
                CREATE TABLE IF NOT EXISTS afk_daily_stats (
                    user_id INTEGER,
                    guild_id INTEGER,
                    date TEXT,
                    total_afk_time INTEGER DEFAULT 0,
                    message_count INTEGER DEFAULT 0,
                    sessions_count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id, date)
                )
            ''')
            
            # Tabella per statistiche AFK totali
            await db.execute('''
                CREATE TABLE IF NOT EXISTS afk_total_stats (
                    user_id INTEGER,
                    guild_id INTEGER,
                    total_afk_time INTEGER DEFAULT 0,
                    total_message_count INTEGER DEFAULT 0,
                    total_sessions_count INTEGER DEFAULT 0,
                    last_reset TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            await db.commit()
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Avvia i task quando il bot è pronto"""
        await self.init_db()
        if not self.reset_daily_stats.is_running():
            self.reset_daily_stats.start()
        print("✅ Sistema AFK pronto!")
    
    @tasks.loop(time=datetime.time(hour=0, minute=0, second=0))  # Mezzanotte
    async def reset_daily_stats(self):
        """Resetta le statistiche giornaliere ogni giorno a mezzanotte"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            print(f"🔄 Reset statistiche AFK giornaliere per il {today}")
            
            async with aiosqlite.connect('database.db') as db:
                # Archivia le statistiche del giorno precedente
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                
                # Copia le statistiche giornaliere nella tabella totale
                await db.execute('''
                    INSERT OR REPLACE INTO afk_total_stats 
                    (user_id, guild_id, total_afk_time, total_message_count, total_sessions_count, last_reset)
                    SELECT 
                        user_id, 
                        guild_id,
                        COALESCE((SELECT total_afk_time FROM afk_total_stats WHERE user_id = ds.user_id AND guild_id = ds.guild_id), 0) + ds.total_afk_time,
                        COALESCE((SELECT total_message_count FROM afk_total_stats WHERE user_id = ds.user_id AND guild_id = ds.guild_id), 0) + ds.message_count,
                        COALESCE((SELECT total_sessions_count FROM afk_total_stats WHERE user_id = ds.user_id AND guild_id = ds.guild_id), 0) + ds.sessions_count,
                        datetime('now')
                    FROM afk_daily_stats ds 
                    WHERE date = ?
                ''', (yesterday,))
                
                # Svuota la tabella delle statistiche giornaliere
                await db.execute('DELETE FROM afk_daily_stats WHERE date = ?', (yesterday,))
                
                await db.commit()
                print(f"✅ Statistiche AFK reset per il {yesterday}")
                
        except Exception as e:
            print(f"❌ Errore reset statistiche AFK: {e}")
    
    @reset_daily_stats.before_loop
    async def before_reset_daily_stats(self):
        """Aspetta che il bot sia pronto prima di avviare il task"""
        await self.bot.wait_until_ready()
    
    async def update_daily_stats(self, user_id: int, guild_id: int, afk_time: int, messages: int = 0, new_session: bool = False):
        """Aggiorna le statistiche giornaliere"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            async with aiosqlite.connect('database.db') as db:
                # Controlla se esiste già una entry per oggi
                async with db.execute('''
                    SELECT total_afk_time, message_count, sessions_count 
                    FROM afk_daily_stats 
                    WHERE user_id = ? AND guild_id = ? AND date = ?
                ''', (user_id, guild_id, today)) as cursor:
                    existing = await cursor.fetchone()
                
                if existing:
                    # Aggiorna la entry esistente
                    current_time, current_messages, current_sessions = existing
                    new_time = current_time + afk_time
                    new_messages = current_messages + messages
                    new_sessions = current_sessions + (1 if new_session else 0)
                    
                    await db.execute('''
                        UPDATE afk_daily_stats 
                        SET total_afk_time = ?, message_count = ?, sessions_count = ?
                        WHERE user_id = ? AND guild_id = ? AND date = ?
                    ''', (new_time, new_messages, new_sessions, user_id, guild_id, today))
                else:
                    # Crea una nuova entry
                    await db.execute('''
                        INSERT INTO afk_daily_stats 
                        (user_id, guild_id, date, total_afk_time, message_count, sessions_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, guild_id, today, afk_time, messages, 1 if new_session else 0))
                
                await db.commit()
                
        except Exception as e:
            print(f"❌ Errore aggiornamento statistiche giornaliere: {e}")
    
    @app_commands.command(name="afk", description="Imposta il tuo status AFK")
    @app_commands.describe(reason="Motivo per cui sei AFK")
    async def afk(self, interaction: discord.Interaction, reason: str = "AFK"):
        """Imposta lo status AFK"""
        await self.init_db()
        
        try:
            async with aiosqlite.connect('database.db') as db:
                # Controlla se l'utente è già AFK
                async with db.execute('SELECT * FROM afk_sessions WHERE user_id = ? AND guild_id = ?', 
                                    (interaction.user.id, interaction.guild.id)) as cursor:
                    existing_afk = await cursor.fetchone()
                
                if existing_afk:
                    # Disattiva lo status AFK esistente
                    await db.execute('DELETE FROM afk_sessions WHERE user_id = ? AND guild_id = ?', 
                                   (interaction.user.id, interaction.guild.id))
                    
                    # Calcola il tempo AFK di questa sessione
                    start_time = datetime.fromisoformat(existing_afk[3])
                    session_duration = int((datetime.now() - start_time).total_seconds())
                    message_count = existing_afk[4] or 0
                    
                    # Aggiorna le statistiche
                    await self.update_daily_stats(
                        interaction.user.id, 
                        interaction.guild.id, 
                        session_duration, 
                        message_count
                    )
                    
                    await db.commit()
                    
                    embed = discord.Embed(
                        title="✅ AFK Disattivato",
                        description=f"Ho rimosso il tuo status AFK.\n**Durata sessione:** {self.format_time(session_duration)}",
                        color=0x00ff00
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    
                else:
                    # Imposta nuovo status AFK
                    await db.execute(
                        'INSERT OR REPLACE INTO afk_sessions (user_id, guild_id, reason, start_time, message_count) VALUES (?, ?, ?, ?, ?)',
                        (interaction.user.id, interaction.guild.id, reason, datetime.now().isoformat(), 0)
                    )
                    await db.commit()
                    
                    embed = discord.Embed(
                        title="⏰ AFK Attivato",
                        description=f"**Motivo:** {reason}",
                        color=0xffff00
                    )
                    embed.set_footer(text="Il tuo status AFK verrà rimosso automaticamente quando scriverai un messaggio")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Gestisce i messaggi per il sistema AFK"""
        if message.author.bot or not message.guild:
            return
        
        await self.init_db()
        
        try:
            async with aiosqlite.connect('database.db') as db:
                # Controlla se l'autore del messaggio è AFK
                async with db.execute('SELECT * FROM afk_sessions WHERE user_id = ? AND guild_id = ?', 
                                    (message.author.id, message.guild.id)) as cursor:
                    user_afk = await cursor.fetchone()
                
                # Se l'autore è AFK, disattiva lo status
                if user_afk:
                    await db.execute('DELETE FROM afk_sessions WHERE user_id = ? AND guild_id = ?', 
                                   (message.author.id, message.guild.id))
                    
                    # Calcola il tempo AFK di questa sessione
                    start_time = datetime.fromisoformat(user_afk[3])
                    session_duration = int((datetime.now() - start_time).total_seconds())
                    message_count = user_afk[4] or 0
                    
                    # Aggiorna le statistiche
                    await self.update_daily_stats(
                        message.author.id, 
                        message.guild.id, 
                        session_duration, 
                        message_count,
                        new_session=True
                    )
                    
                    await db.commit()
                    
                    # Messaggio di benvenuto solo se la sessione AFK era abbastanza lunga
                    if session_duration > 30:  # Almeno 30 secondi
                        welcome_embed = discord.Embed(
                            title="👋 Bentornato!",
                            description=f"Ho rimosso il tuo status AFK.\n**Eri AFK per:** {self.format_time(session_duration)}",
                            color=0x00ff00
                        )
                        await message.channel.send(embed=welcome_embed, delete_after=10)
                
                # Controlla se il messaggio menziona qualcuno che è AFK
                for mention in message.mentions:
                    async with db.execute('SELECT * FROM afk_sessions WHERE user_id = ? AND guild_id = ?', 
                                        (mention.id, message.guild.id)) as cursor:
                        mentioned_afk = await cursor.fetchone()
                    
                    if mentioned_afk and mention.id != message.author.id:
                        reason = mentioned_afk[2]  # reason
                        start_time = datetime.fromisoformat(mentioned_afk[3])  # start_time
                        afk_duration = datetime.now() - start_time
                        
                        # Incrementa il contatore messaggi per la persona AFK
                        current_count = mentioned_afk[4] or 0
                        new_count = current_count + 1
                        
                        await db.execute(
                            'UPDATE afk_sessions SET message_count = ? WHERE user_id = ? AND guild_id = ?',
                            (new_count, mention.id, message.guild.id)
                        )
                        await db.commit()
                        
                        # Messaggio di notifica AFK
                        afk_embed = discord.Embed(
                            title="⏰ Utente AFK",
                            description=f"**{mention.display_name}** è attualmente AFK",
                            color=0xffff00
                        )
                        afk_embed.add_field(
                            name="📝 Motivo",
                            value=reason,
                            inline=False
                        )
                        afk_embed.add_field(
                            name="⏱️ Durata",
                            value=self.format_time(int(afk_duration.total_seconds())),
                            inline=True
                        )
                        afk_embed.set_footer(text="Verrà notificato al suo ritorno")
                        
                        await message.channel.send(embed=afk_embed, delete_after=15)
                        
        except Exception as e:
            print(f"Errore sistema AFK: {e}")
    
    @app_commands.command(name="afk_leaderboard", description="Mostra la classifica AFK giornaliera")
    async def afk_leaderboard(self, interaction: discord.Interaction):
        """Mostra la leaderboard AFK giornaliera"""
        await self.init_db()
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            async with aiosqlite.connect('database.db') as db:
                # Classifica per tempo AFK giornaliero
                async with db.execute('''
                    SELECT user_id, total_afk_time, message_count 
                    FROM afk_daily_stats 
                    WHERE guild_id = ? AND date = ?
                    ORDER BY total_afk_time DESC 
                    LIMIT 10
                ''', (interaction.guild.id, today)) as cursor:
                    daily_leaderboard = await cursor.fetchall()
            
            embed = discord.Embed(
                title="🏆 Classifica AFK - Oggi",
                color=0xffd700,
                timestamp=datetime.now()
            )
            
            if not daily_leaderboard:
                embed.description = "Nessun dato AFK per oggi!\nUsa `/afk` per impostare il tuo status."
            else:
                description = ""
                for index, (user_id, total_time, total_mentions) in enumerate(daily_leaderboard, 1):
                    user = interaction.guild.get_member(user_id)
                    username = user.display_name if user else f"Utente Sconosciuto ({user_id})"
                    
                    emoji = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"{index}."
                    
                    description += (
                        f"{emoji} **{username}**\n"
                        f"   ⏰ Tempo AFK: `{self.format_time(total_time)}`\n"
                        f"   👥 Mention: `{total_mentions}`\n\n"
                    )
                
                embed.description = description
            
            embed.set_footer(text=f"Classifica giornaliera • {interaction.guild.name}")
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    @app_commands.command(name="afk_leaderboard_total", description="Mostra la classifica AFK totale")
    async def afk_leaderboard_total(self, interaction: discord.Interaction):
        """Mostra la leaderboard AFK totale di sempre"""
        await self.init_db()
        
        try:
            async with aiosqlite.connect('database.db') as db:
                # Classifica per tempo AFK totale
                async with db.execute('''
                    SELECT user_id, total_afk_time, total_message_count 
                    FROM afk_total_stats 
                    WHERE guild_id = ?
                    ORDER BY total_afk_time DESC 
                    LIMIT 10
                ''', (interaction.guild.id,)) as cursor:
                    total_leaderboard = await cursor.fetchall()
            
            embed = discord.Embed(
                title="🏆 Classifica AFK - Totale",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            if not total_leaderboard:
                embed.description = "Nessun dato AFK totale disponibile!"
            else:
                description = ""
                for index, (user_id, total_time, total_mentions) in enumerate(total_leaderboard, 1):
                    user = interaction.guild.get_member(user_id)
                    username = user.display_name if user else f"Utente Sconosciuto ({user_id})"
                    
                    emoji = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"{index}."
                    
                    description += (
                        f"{emoji} **{username}**\n"
                        f"   ⏰ Tempo Totale: `{self.format_time(total_time)}`\n"
                        f"   👥 Mention Totali: `{total_mentions}`\n\n"
                    )
                
                embed.description = description
            
            embed.set_footer(text=f"Classifica totale • {interaction.guild.name}")
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    @app_commands.command(name="afk_stats", description="Mostra le tue statistiche AFK")
    async def afk_stats(self, interaction: discord.Interaction):
        """Mostra le statistiche AFK personali"""
        await self.init_db()
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            async with aiosqlite.connect('database.db') as db:
                # Statistiche giornaliere
                async with db.execute('''
                    SELECT total_afk_time, message_count, sessions_count 
                    FROM afk_daily_stats 
                    WHERE user_id = ? AND guild_id = ? AND date = ?
                ''', (interaction.user.id, interaction.guild.id, today)) as cursor:
                    daily_stats = await cursor.fetchone()
                
                # Statistiche totali
                async with db.execute('''
                    SELECT total_afk_time, total_message_count, total_sessions_count 
                    FROM afk_total_stats 
                    WHERE user_id = ? AND guild_id = ?
                ''', (interaction.user.id, interaction.guild.id)) as cursor:
                    total_stats = await cursor.fetchone()
                
                # Sessioni AFK attive
                async with db.execute('''
                    SELECT reason, start_time 
                    FROM afk_sessions 
                    WHERE user_id = ? AND guild_id = ?
                ''', (interaction.user.id, interaction.guild.id)) as cursor:
                    current_afk = await cursor.fetchone()
            
            daily_time = daily_stats[0] if daily_stats else 0
            daily_mentions = daily_stats[1] if daily_stats else 0
            daily_sessions = daily_stats[2] if daily_stats else 0
            
            total_time = total_stats[0] if total_stats else 0
            total_mentions = total_stats[1] if total_stats else 0
            total_sessions = total_stats[2] if total_stats else 0
            
            embed = discord.Embed(
                title="📊 Le tue Statistiche AFK",
                color=0x0099ff
            )
            
            # Statistiche giornaliere
            embed.add_field(
                name="📅 OGGI",
                value=(
                    f"⏰ Tempo: `{self.format_time(daily_time)}`\n"
                    f"👥 Mention: `{daily_mentions}`\n"
                    f"🔄 Sessioni: `{daily_sessions}`"
                ),
                inline=True
            )
            
            # Statistiche totali
            embed.add_field(
                name="🏆 TOTALI",
                value=(
                    f"⏰ Tempo: `{self.format_time(total_time)}`\n"
                    f"👥 Mention: `{total_mentions}`\n"
                    f"🔄 Sessioni: `{total_sessions}`"
                ),
                inline=True
            )
            
            # Status attuale
            if current_afk:
                reason, start_time = current_afk
                afk_duration = datetime.now() - datetime.fromisoformat(start_time)
                
                embed.add_field(
                    name="🟢 STATUS ATTUALE",
                    value=(
                        f"**AFK Attivo**\n"
                        f"📝 {reason}\n"
                        f"⏱️ {self.format_time(int(afk_duration.total_seconds()))}"
                    ),
                    inline=False
                )
            else:
                embed.add_field(
                    name="🔴 STATUS ATTUALE",
                    value="**Non AFK**",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    def format_time(self, seconds: int) -> str:
        """Formatta il tempo in una stringa leggibile"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}g {hours}h"

async def setup(bot):
    await bot.add_cog(AFKSystem(bot))
