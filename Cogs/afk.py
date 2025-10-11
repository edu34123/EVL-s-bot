import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import aiosqlite
from datetime import datetime, timedelta

class AFKSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}  # Cache per utenti AFK
        self.LEADERBOARD_CHANNEL_ID = 1426606478273286264  # Canale per la leaderboard automatica
        self.leaderboard_task = None
    
    async def init_db(self):
        """Inizializza la tabella AFK nel database"""
        async with aiosqlite.connect('database.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS afk_users (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    reason TEXT,
                    start_time TEXT,
                    auto_end BOOLEAN DEFAULT TRUE,
                    total_afk_time INTEGER DEFAULT 0
                )
            ''')
            await db.commit()
    
    async def load_afk_users(self):
        """Carica gli utenti AFK dal database"""
        async with aiosqlite.connect('database.db') as db:
            async with db.execute('SELECT user_id, guild_id, reason, start_time, auto_end FROM afk_users') as cursor:
                rows = await cursor.fetchall()
                
        for row in rows:
            user_id, guild_id, reason, start_time, auto_end = row
            self.afk_users[user_id] = {
                'guild_id': guild_id,
                'reason': reason,
                'start_time': datetime.fromisoformat(start_time),
                'auto_end': bool(auto_end)
            }
    
    async def start_leaderboard_updates(self):
        """Avvia gli aggiornamenti automatici della leaderboard"""
        # Avvia il task per gli aggiornamenti periodici
        self.leaderboard_task = self.bot.loop.create_task(self.auto_leaderboard_update())
    
    async def auto_leaderboard_update(self):
        """Aggiorna automaticamente la leaderboard ogni 24 ore"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                # Aspetta fino alle 20:00 (8 PM) del giorno successivo
                now = datetime.now()
                target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
                
                if now >= target_time:
                    target_time += timedelta(days=1)
                
                wait_seconds = (target_time - now).total_seconds()
                print(f"⏰ Prossimo aggiornamento leaderboard AFK tra {wait_seconds/3600:.1f} ore")
                
                await asyncio.sleep(wait_seconds)
                
                # Invia la leaderboard
                await self.send_auto_leaderboard()
                
                # Aspetta 24 ore prima del prossimo aggiornamento
                await asyncio.sleep(86400)  # 24 ore
                
            except Exception as e:
                print(f"❌ Errore nell'aggiornamento automatico leaderboard: {e}")
                await asyncio.sleep(3600)  # Aspetta 1 ora in caso di errore
    
    async def send_auto_leaderboard(self):
        """Invia la leaderboard automatica nel canale designato"""
        try:
            channel = self.bot.get_channel(self.LEADERBOARD_CHANNEL_ID)
            if not channel:
                print(f"❌ Canale leaderboard {self.LEADERBOARD_CHANNEL_ID} non trovato!")
                return
            
            # Recupera i dati della leaderboard
            async with aiosqlite.connect('database.db') as db:
                async with db.execute(
                    'SELECT user_id, total_afk_time FROM afk_users ORDER BY total_afk_time DESC LIMIT 10'
                ) as cursor:
                    rows = await cursor.fetchall()
            
            if not rows:
                # Nessun dato AFK, invia un messaggio comunque
                embed = discord.Embed(
                    title="🏆 Classifica Tempi AFK - Giornaliera",
                    color=0xffd700,
                    description="*Nessun dato AFK disponibile al momento*"
                )
                embed.set_footer(text="Aggiornamento automatico giornaliero • Usa /afk per impostare il tuo stato AFK")
                await channel.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="🏆 Classifica Tempi AFK - Giornaliera",
                color=0xffd700,
                description="**Utenti con più tempo totale in AFK**\n*Aggiornamento automatico ogni 24 ore*"
            )
            
            leaderboard_text = ""
            for i, (user_id, total_seconds) in enumerate(rows, 1):
                user = self.bot.get_user(user_id)
                username = user.mention if user else f"👤 Utente Sconosciuto"
                
                medal = ""
                if i == 1: medal = "🥇 "
                elif i == 2: medal = "🥈 "
                elif i == 3: medal = "🥉 "
                else: medal = "🔹 "
                
                time_str = self.format_total_time(total_seconds)
                leaderboard_text += f"{medal} **{i}.** {username} - `{time_str}`\n"
            
            embed.add_field(
                name="Top 10 AFK", 
                value=leaderboard_text or "Nessun dato disponibile", 
                inline=False
            )
            
            # Aggiungi statistiche aggiuntive
            total_users = len(rows)
            total_time_all = sum(row[1] for row in rows)
            avg_time = total_time_all / total_users if total_users > 0 else 0
            
            embed.add_field(
                name="📊 Statistiche",
                value=f"• **Utenti totali:** {total_users}\n• **Tempo medio:** `{self.format_total_time(int(avg_time))}`\n• **Tempo totale:** `{self.format_total_time(total_time_all)}`",
                inline=False
            )
            
            embed.set_footer(text="Aggiornamento automatico giornaliero • Usa /afk per impostare il tuo stato AFK")
            
            await channel.send(embed=embed)
            print("✅ Leaderboard AFK automatica inviata!")
            
        except Exception as e:
            print(f"❌ Errore nell'invio della leaderboard automatica: {e}")
    
    @app_commands.command(name="afk", description="Gestisci il tuo stato AFK")
    @app_commands.describe(
        action="Azione da eseguire",
        reason="Motivo dell'AFK",
        auto_end="Disabilita auto-rimozione quando scrivi"
    )
    async def afk(self, interaction: discord.Interaction, action: str, reason: str = "Nessun motivo fornito", auto_end: bool = True):
        """Sistema AFK con gestione completa"""
        
        if action.lower() == "start":
            await self.afk_start(interaction, reason, auto_end)
        elif action.lower() == "end":
            await self.afk_end(interaction)
        else:
            await interaction.response.send_message("❌ Azione non valida! Usa `start` o `end`.", ephemeral=True)
    
    async def afk_start(self, interaction: discord.Interaction, reason: str, auto_end: bool):
        """Attiva lo stato AFK"""
        user_id = interaction.user.id
        
        # Controlla se l'utente è già AFK
        if user_id in self.afk_users:
            await interaction.response.send_message("❌ Sei già in stato AFK!", ephemeral=True)
            return
        
        start_time = datetime.now()
        
        # Salva nel database
        async with aiosqlite.connect('database.db') as db:
            await db.execute(
                'INSERT OR REPLACE INTO afk_users (user_id, guild_id, reason, start_time, auto_end) VALUES (?, ?, ?, ?, ?)',
                (user_id, interaction.guild.id, reason, start_time.isoformat(), auto_end)
            )
            await db.commit()
        
        # Aggiorna cache
        self.afk_users[user_id] = {
            'guild_id': interaction.guild.id,
            'reason': reason,
            'start_time': start_time,
            'auto_end': auto_end
        }
        
        # Modifica nickname per mostrare AFK
        try:
            new_nickname = f"[AFK] {interaction.user.display_name}"
            if len(new_nickname) <= 32:  # Limite caratteri Discord
                await interaction.user.edit(nick=new_nickname)
        except discord.Forbidden:
            pass  # Non ha i permessi per modificare il nickname
        
        # Crea embed di risposta
        embed = discord.Embed(
            title="🚶‍♂️ Stato AFK Attivato",
            color=0x00ff00,
            description=f"**{interaction.user.mention} è ora AFK**"
        )
        embed.add_field(name="📝 Motivo", value=reason, inline=False)
        embed.add_field(name="⏰ Orario di inizio", value=f"<t:{int(start_time.timestamp())}:R>", inline=True)
        embed.add_field(name="🔧 Auto End", value="✅ Attivo" if auto_end else "❌ Disattivo", inline=True)
        embed.set_footer(text="Scrivi un messaggio per disattivare l'AFK (se auto-end è attivo)")
        
        await interaction.response.send_message(embed=embed)
    
    async def afk_end(self, interaction: discord.Interaction):
        """Disattiva lo stato AFK"""
        user_id = interaction.user.id
        
        # Controlla se l'utente è AFK
        if user_id not in self.afk_users:
            await interaction.response.send_message("❌ Non sei in stato AFK!", ephemeral=True)
            return
        
        afk_data = self.afk_users[user_id]
        start_time = afk_data['start_time']
        end_time = datetime.now()
        afk_duration = end_time - start_time
        
        # Calcola tempo totale AFK per la leaderboard
        total_seconds = int(afk_duration.total_seconds())
        
        # Aggiorna tempo totale nel database
        async with aiosqlite.connect('database.db') as db:
            # Recupera il tempo totale precedente
            async with db.execute('SELECT total_afk_time FROM afk_users WHERE user_id = ?', (user_id,)) as cursor:
                result = await cursor.fetchone()
                previous_total = result[0] if result else 0
            
            new_total = previous_total + total_seconds
            
            # Aggiorna tempo totale e rimuove dall'AFK
            await db.execute(
                'UPDATE afk_users SET total_afk_time = ? WHERE user_id = ?',
                (new_total, user_id)
            )
            await db.execute('DELETE FROM afk_users WHERE user_id = ?', (user_id,))
            await db.commit()
        
        # Rimuovi dalla cache
        del self.afk_users[user_id]
        
        # Ripristina nickname
        try:
            original_nick = interaction.user.display_name.replace("[AFK] ", "").replace("[AFK]", "").strip()
            if original_nick != interaction.user.display_name:
                await interaction.user.edit(nick=original_nick if original_nick else None)
        except discord.Forbidden:
            pass
        
        # Formatta durata
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        duration_str = ""
        if hours > 0:
            duration_str += f"{hours}h "
        if minutes > 0:
            duration_str += f"{minutes}m "
        duration_str += f"{seconds}s"
        
        # Embed di risposta
        embed = discord.Embed(
            title="✅ Stato AFK Disattivato",
            color=0x00ff00,
            description=f"**Bentornato {interaction.user.mention}!**"
        )
        embed.add_field(name="⏱️ Durata AFK", value=duration_str, inline=True)
        embed.add_field(name="📊 Tempo totale AFK", value=self.format_total_time(new_total), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="afk_leaderboard", description="Classifica dei tempi AFK")
    async def afk_leaderboard(self, interaction: discord.Interaction):
        """Mostra la leaderboard dei tempi AFK"""
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(
                'SELECT user_id, total_afk_time FROM afk_users ORDER BY total_afk_time DESC LIMIT 10'
            ) as cursor:
                rows = await cursor.fetchall()
        
        if not rows:
            await interaction.response.send_message("📊 Nessun dato AFK disponibile!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏆 Classifica Tempi AFK",
            color=0xffd700,
            description="Utenti con più tempo totale in AFK"
        )
        
        leaderboard_text = ""
        for i, (user_id, total_seconds) in enumerate(rows, 1):
            user = self.bot.get_user(user_id)
            username = user.mention if user else f"👤 Utente Sconosciuto"
            
            medal = ""
            if i == 1: medal = "🥇 "
            elif i == 2: medal = "🥈 "
            elif i == 3: medal = "🥉 "
            else: medal = "🔹 "
            
            time_str = self.format_total_time(total_seconds)
            leaderboard_text += f"{medal} **{i}.** {username} - `{time_str}`\n"
        
        embed.add_field(name="Top 10 AFK", value=leaderboard_text, inline=False)
        
        # Aggiungi statistiche
        total_users = len(rows)
        total_time_all = sum(row[1] for row in rows)
        avg_time = total_time_all / total_users if total_users > 0 else 0
        
        embed.add_field(
            name="📊 Statistiche",
            value=f"• **Utenti totali:** {total_users}\n• **Tempo medio:** `{self.format_total_time(int(avg_time))}`\n• **Tempo totale:** `{self.format_total_time(total_time_all)}`",
            inline=False
        )
        
        embed.set_footer(text="Aggiornamento automatico giornaliero alle 20:00")
        
        await interaction.response.send_message(embed=embed)
    
    def format_total_time(self, total_seconds: int) -> str:
        """Formatta il tempo totale in una stringa leggibile"""
        if total_seconds == 0:
            return "0s"
        
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_parts = []
        if days > 0:
            time_parts.append(f"{days}g")
        if hours > 0:
            time_parts.append(f"{hours}h")
        if minutes > 0:
            time_parts.append(f"{minutes}m")
        if seconds > 0 and days == 0:  # Mostra secondi solo se meno di un giorno
            time_parts.append(f"{seconds}s")
        
        return " ".join(time_parts)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Gestisce l'auto-rimozione AFK quando l'utente scrive"""
        if message.author.bot or not message.guild:
            return
        
        user_id = message.author.id
        
        # Controlla se l'utente è AFK
        if user_id in self.afk_users:
            afk_data = self.afk_users[user_id]
            
            # Auto-end solo se abilitato
            if afk_data['auto_end']:
                await self.remove_afk_auto(message.author, message.channel)
    
    async def remove_afk_auto(self, user: discord.Member, channel):
        """Rimuove automaticamente l'AFK quando l'utente scrive"""
        user_id = user.id
        afk_data = self.afk_users[user_id]
        start_time = afk_data['start_time']
        end_time = datetime.now()
        afk_duration = end_time - start_time
        
        total_seconds = int(afk_duration.total_seconds())
        
        # Aggiorna database
        async with aiosqlite.connect('database.db') as db:
            async with db.execute('SELECT total_afk_time FROM afk_users WHERE user_id = ?', (user_id,)) as cursor:
                result = await cursor.fetchone()
                previous_total = result[0] if result else 0
            
            new_total = previous_total + total_seconds
            
            await db.execute(
                'UPDATE afk_users SET total_afk_time = ? WHERE user_id = ?',
                (new_total, user_id)
            )
            await db.execute('DELETE FROM afk_users WHERE user_id = ?', (user_id,))
            await db.commit()
        
        # Rimuovi dalla cache
        del self.afk_users[user_id]
        
        # Ripristina nickname
        try:
            original_nick = user.display_name.replace("[AFK] ", "").replace("[AFK]", "").strip()
            if original_nick != user.display_name:
                await user.edit(nick=original_nick if original_nick else None)
        except discord.Forbidden:
            pass
        
        # Notifica nel canale
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        duration_str = ""
        if hours > 0:
            duration_str += f"{hours}h "
        if minutes > 0:
            duration_str += f"{minutes}m "
        duration_str += f"{seconds}s"
        
        embed = discord.Embed(
            description=f"✅ {user.mention} non è più AFK (durata: `{duration_str}`)",
            color=0x00ff00
        )
        await channel.send(embed=embed, delete_after=10)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Ricarica gli AFK quando il bot si riavvia"""
        await self.load_afk_users()
    
    async def cog_load(self):
        """Carica i dati AFK all'avvio del cog"""
        await self.init_db()
        await self.load_afk_users()
        await self.start_leaderboard_updates()
        print("✅ Sistema AFK caricato! Leaderboard automatica attivata.")
    
    async def cog_unload(self):
        """Ferma i task quando il cog viene scaricato"""
        if self.leaderboard_task:
            self.leaderboard_task.cancel()
        print("❌ Sistema AFK scaricato.")

async def setup(bot):
    await bot.add_cog(AFKSystem(bot))
