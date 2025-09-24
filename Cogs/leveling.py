import discord
from discord.ext import commands, tasks
import asyncio
import aiosqlite
import os
import random
from datetime import datetime, timedelta

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = {}
        
        # Configurazione leaderboard automatica
        self.LEVEL_CHANNEL_ID = int(os.getenv('LEVEL_LEADERBOARD_CHANNEL_ID', '1392483787384029294'))
        self.leaderboard_message_id = None
        
        # Configurazione progressione livelli con 6,000,000 XP massimo
        self.level_requirements = {
            1: 0,        # Livello 1: base
            2: 100,      # Livello 2: 100 XP
            3: 300,      # Livello 3: 300 XP
            # ... (mantieni tutti i livelli esistenti)
            300: 7110000  # Livello 300: 7,110,000 XP (oltre i 6M richiesti)
        }
        
        # Ruoli per ogni livello
        self.level_roles = {
            5: int(os.getenv('LEVEL_5_ROLE', '1392732183671738471')),
            10: int(os.getenv('LEVEL_10_ROLE', '1392732172460228618')),
            # ... (mantieni tutti i ruoli esistenti)
            300: int(os.getenv('LEVEL_300_ROLE', '1419373736728985772'))
        }

    def cog_unload(self):
        """Ferma il task quando il cog viene scaricato"""
        self.update_leaderboard.cancel()

    @tasks.loop(minutes=30)
    async def update_leaderboard(self):
        """Task automatico per aggiornare la leaderboard - ELIMINA MESSAGGI VECCHI"""
        if self.LEVEL_CHANNEL_ID == 0:
            return
            
        try:
            for guild in self.bot.guilds:
                channel = guild.get_channel(self.LEVEL_CHANNEL_ID)
                if channel:
                    await self.send_or_update_leaderboard(channel)
                    break
        except Exception as e:
            print(f"❌ Errore aggiornamento leaderboard automatico: {e}")

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        """Aspetta che il bot sia pronto prima di iniziare il task"""
        await self.bot.wait_until_ready()

    async def send_or_update_leaderboard(self, channel):
        """Invia o aggiorna la leaderboard nel canale - ELIMINA MESSAGGI VECCHI"""
        try:
            # 🔥 ELIMINA TUTTI I MESSAGGI VECCHI DEL BOT NEL CANALE
            async for message in channel.history(limit=30):
                if message.author == self.bot.user:
                    try:
                        await message.delete()
                        await asyncio.sleep(0.3)  # Pausa per evitare rate limit
                    except:
                        pass
            
            await asyncio.sleep(2)
            
            # CREA E INVIA LA NUOVA LEADERBOARD
            embed = await self.create_leaderboard_embed(channel.guild)
            
            # 🔥 INVIA L'EMBED DELLA CLASSIFICA
            message = await channel.send(embed=embed)
            self.leaderboard_message_id = message.id
            
            # 🔥 INVIA I PULSANTI IN UN MESSAGGIO SEPARATO SOTTO
            view = discord.ui.View(timeout=None)
            
            # Pulsante refresh leaderboard
            refresh_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="🔄 Aggiorna Classifica",
                custom_id="refresh_leaderboard"
            )
            
            async def refresh_callback(interaction):
                if not interaction.user.guild_permissions.administrator:
                    await interaction.response.send_message("❌ Solo gli admin possono aggiornare la classifica!", ephemeral=True)
                    return
                    
                await interaction.response.defer()
                
                # Elimina tutti i messaggi vecchi
                async for message in channel.history(limit=20):
                    if message.author == self.bot.user:
                        try:
                            await message.delete()
                            await asyncio.sleep(0.3)
                        except:
                            pass
                
                await asyncio.sleep(2)
                await self.send_or_update_leaderboard(channel)
                await interaction.followup.send("✅ Classifica aggiornata!", ephemeral=True)
            
            refresh_button.callback = refresh_callback
            view.add_item(refresh_button)
            
            # Pulsante per vedere il proprio livello
            level_button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="📊 Vedi il Mio Livello",
                custom_id="my_level"
            )
            
            async def level_callback(interaction):
                try:
                    async with aiosqlite.connect('database.db') as db:
                        cursor = await db.execute(
                            'SELECT xp, level, messages FROM levels WHERE user_id = ? AND guild_id = ?',
                            (interaction.user.id, interaction.guild.id)
                        )
                        result = await cursor.fetchone()
                        
                        if result:
                            xp, level, messages = result
                            required_xp = self.get_required_xp(level + 1)
                            xp_current_level = xp - self.get_required_xp(level)
                            xp_needed = required_xp - xp
                            xp_for_next_level = required_xp - self.get_required_xp(level)
                            
                            if xp_for_next_level > 0:
                                progress = (xp_current_level / xp_for_next_level) * 100
                            else:
                                progress = 100
                            
                            embed = discord.Embed(
                                title=f"📊 Il Tuo Livello",
                                color=0x0099ff
                            )
                            embed.set_thumbnail(url=interaction.user.display_avatar.url)
                            
                            embed.add_field(name="Livello", value=f"**{level}**", inline=True)
                            embed.add_field(name="XP Totale", value=f"**{xp:,}** XP", inline=True)
                            embed.add_field(name="Messaggi", value=f"**{messages}**", inline=True)
                            
                            if progress < 100:
                                embed.add_field(
                                    name="Progresso",
                                    value=f"`{self.create_progress_bar(progress)}`\n"
                                          f"**{xp_current_level:,}**/{xp_for_next_level:,} XP "
                                          f"({progress:.1f}%)",
                                    inline=False
                                )
                                
                                embed.add_field(
                                    name="Prossimo Livello",
                                    value=f"**Livello {level + 1}** in **{xp_needed:,}** XP",
                                    inline=False
                                )
                            else:
                                embed.add_field(
                                    name="Status",
                                    value="🎉 Livello Massimo Raggiunto!",
                                    inline=False
                                )
                            
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                        else:
                            await interaction.response.send_message(
                                "❌ Non hai ancora accumulato XP! Scrivi qualche messaggio per salire di livello.",
                                ephemeral=True
                            )
                            
                except Exception as e:
                    print(f"❌ Errore pulsante livello: {e}")
                    await interaction.response.send_message("❌ Errore nel recuperare i dati.", ephemeral=True)
            
            level_button.callback = level_callback
            view.add_item(level_button)
            
            # 🔥 INVIA I PULSANTI IN UN MESSAGGIO SEPARATO DOPO L'EMBED
            await channel.send(
                "**Gestione Classifica:**",
                view=view
            )
            
            print("✅ Leaderboard aggiornata e inviata")
            
        except Exception as e:
            print(f"❌ Errore invio/aggiornamento leaderboard: {e}")

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
                    username = user.display_name if user else f"❓ Utente Sconosciuto"
                    
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
                
                total_users = len(results)
                total_xp = sum(xp for _, xp, _, _ in results)
                avg_level = sum(level for _, _, level, _ in results) / total_users
                
                embed.add_field(
                    name="📈 Statistiche Server",
                    value=(
                        f"• **Utenti in classifica:** {total_users}\n"
                        f"• **XP totale:** {total_xp:,}\n"
                        f"• **Livello medio:** {avg_level:.1f}\n"
                        f"• **Ultimo aggiornamento:** <t:{int(datetime.now().timestamp())}:R>"
                    ),
                    inline=False
                )
                
                embed.set_footer(
                    text="Classifica aggiornata automaticamente ogni 30 minuti • Usa >level per vedere il tuo livello"
                )
                
                return embed
                
        except Exception as e:
            print(f"❌ Errore creazione embed leaderboard: {e}")
            embed = discord.Embed(
                title="❌ Errore Classifica",
                description="Si è verificato un errore nel caricare la classifica.",
                color=0xff0000
            )
            return embed

    async def update_leaderboard_now(self):
        """Aggiorna immediatamente la leaderboard"""
        try:
            for guild in self.bot.guilds:
                channel = guild.get_channel(self.LEVEL_CHANNEL_ID)
                if channel:
                    await self.send_or_update_leaderboard(channel)
                    break
        except Exception as e:
            print(f"❌ Errore aggiornamento leaderboard immediato: {e}")

    def get_required_xp(self, level):
        """Calcola l'XP required per un dato livello"""
        if level in self.level_requirements:
            return self.level_requirements[level]
        elif level > 300:
            base_xp = 7110000
            additional_levels = level - 300
            return base_xp + (additional_levels * 150000)
        else:
            closest_level = max(lvl for lvl in self.level_requirements.keys() if lvl <= level)
            base_xp = self.level_requirements[closest_level]
            levels_diff = level - closest_level
            return base_xp + (levels_diff * 15000)

    def get_level_from_xp(self, xp):
        """Calcola il livello basato sull'XP"""
        if xp >= 6000000:
            max_level_under_6m = max(lvl for lvl, xp_req in self.level_requirements.items() if xp_req <= 6000000)
            additional_xp = xp - 6000000
            additional_levels = additional_xp // 150000
            return max_level_under_6m + additional_levels
        
        level = 1
        while xp >= self.get_required_xp(level + 1) and level < 1000:
            level += 1
        return level

    @commands.Cog.listener()
    async def on_ready(self):
        """Inizializza il sistema di livelli"""
        print("✅ Sistema di Livelli caricato!")
        print(f"✅ Canale leaderboard: {self.LEVEL_CHANNEL_ID}")
        await self.init_db()
        
        self.update_leaderboard.start()
        
        if self.LEVEL_CHANNEL_ID != 0:
            await asyncio.sleep(5)
            await self.update_leaderboard_now()

    async def init_db(self):
        """Inizializza il database"""
        try:
            async with aiosqlite.connect('database.db') as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS levels (
                        user_id INTEGER PRIMARY KEY,
                        guild_id INTEGER,
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        messages INTEGER DEFAULT 0,
                        last_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                await db.commit()
            print("✅ Database livelli inizializzato!")
        except Exception as e:
            print(f"❌ Errore database livelli: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Gestisce l'XP quando un utente invia un messaggio"""
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        current_time = datetime.now()
        
        if user_id in self.cooldown:
            time_diff = current_time - self.cooldown[user_id]
            if time_diff.total_seconds() < 3:
                return
        
        self.cooldown[user_id] = current_time

        xp_gained = random.randint(15, 25)
        
        try:
            async with aiosqlite.connect('database.db') as db:
                cursor = await db.execute(
                    'SELECT xp, level, messages FROM levels WHERE user_id = ? AND guild_id = ?',
                    (user_id, message.guild.id)
                )
                result = await cursor.fetchone()
                
                if result:
                    current_xp, current_level, messages = result
                    new_xp = current_xp + xp_gained
                    new_level = self.get_level_from_xp(new_xp)
                    new_messages = messages + 1
                    
                    await db.execute(
                        'UPDATE levels SET xp = ?, level = ?, messages = ?, last_message = ? WHERE user_id = ? AND guild_id = ?',
                        (new_xp, new_level, new_messages, current_time, user_id, message.guild.id)
                    )
                    
                    if new_level > current_level:
                        await self.handle_level_up(message, message.author, new_level, new_xp)
                
                else:
                    new_xp = xp_gained
                    new_level = 1
                    await db.execute(
                        'INSERT INTO levels (user_id, guild_id, xp, level, messages, last_message) VALUES (?, ?, ?, ?, ?, ?)',
                        (user_id, message.guild.id, new_xp, new_level, 1, current_time)
                    )
                
                await db.commit()
                
        except Exception as e:
            print(f"❌ Errore aggiornamento XP: {e}")

    async def handle_level_up(self, message, user, new_level, new_xp):
        """Gestisce il livello up"""
        guild = message.guild
        
        if new_level <= 20 or new_level % 5 == 0:
            embed = discord.Embed(
                title="🎉 Livello Up!",
                description=f"{user.mention} è salito al **livello {new_level}**!",
                color=0x00ff00
            )
            embed.add_field(name="XP Totale", value=f"{new_xp:,} XP", inline=True)
            embed.add_field(name="Prossimo Livello", value=f"{self.get_required_xp(new_level + 1):,} XP", inline=True)
            embed.set_thumbnail(url=user.display_avatar.url)
            
            try:
                await message.channel.send(embed=embed, delete_after=10)
            except:
                pass
        
        await self.assign_level_roles(user, new_level, guild)

    async def assign_level_roles(self, user, new_level, guild):
        """Assegna i ruoli in base al livello"""
        try:
            roles_to_assign = []
            for level, role_id in self.level_roles.items():
                if new_level >= level and role_id != 0:
                    role = guild.get_role(role_id)
                    if role and role not in user.roles:
                        roles_to_assign.append(role)
            
            if roles_to_assign:
                await user.add_roles(*roles_to_assign, reason=f"Raggiunto livello {new_level}")
            
        except Exception as e:
            print(f"❌ Errore assegnazione ruoli: {e}")

    @commands.command(name='level', aliases=['lvl', 'rank'])
    async def level_command(self, ctx, user: discord.Member = None):
        """Mostra il livello e XP di un utente"""
        if user is None:
            user = ctx.author
        
        try:
            async with aiosqlite.connect('database.db') as db:
                cursor = await db.execute(
                    'SELECT xp, level, messages FROM levels WHERE user_id = ? AND guild_id = ?',
                    (user.id, ctx.guild.id)
                )
                result = await cursor.fetchone()
                
                if result:
                    xp, level, messages = result
                    required_xp = self.get_required_xp(level + 1)
                    xp_current_level = xp - self.get_required_xp(level)
                    xp_needed = required_xp - xp
                    xp_for_next_level = required_xp - self.get_required_xp(level)
                    
                    if xp_for_next_level > 0:
                        progress = (xp_current_level / xp_for_next_level) * 100
                    else:
                        progress = 100
                    
                    embed = discord.Embed(
                        title=f"📊 Livello di {user.display_name}",
                        color=0x0099ff
                    )
                    embed.set_thumbnail(url=user.display_avatar.url)
                    
                    embed.add_field(name="Livello", value=f"**{level}**", inline=True)
                    embed.add_field(name="XP Totale", value=f"**{xp:,}** XP", inline=True)
                    embed.add_field(name="Messaggi", value=f"**{messages}**", inline=True)
                    
                    if progress < 100:
                        embed.add_field(
                            name="Progresso",
                            value=f"`{self.create_progress_bar(progress)}`\n"
                                  f"**{xp_current_level:,}**/{xp_for_next_level:,} XP "
                                  f"({progress:.1f}%)",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="Prossimo Livello",
                            value=f"**Livello {level + 1}** in **{xp_needed:,}** XP",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="Status",
                            value="🎉 Livello Massimo Raggiunto!",
                            inline=False
                        )
                    
                    await ctx.send(embed=embed)
                    
                else:
                    await ctx.send(f"❌ {user.mention} non ha ancora accumulato XP!")
                    
        except Exception as e:
            print(f"❌ Errore comando level: {e}")
            await ctx.send("❌ Errore nel recuperare i dati del livello.")

    def create_progress_bar(self, percentage, length=20):
        """Crea una barra di progresso"""
        filled = int(length * percentage / 100)
        empty = length - filled
        return "█" * filled + "░" * empty

    @commands.command(name='leaderboard', aliases=['lb', 'top'])
    async def leaderboard_command(self, ctx):
        """Mostra la classifica dei livelli"""
        try:
            embed = await self.create_leaderboard_embed(ctx.guild)
            await ctx.send(embed=embed)
                
        except Exception as e:
            print(f"❌ Errore leaderboard: {e}")
            await ctx.send("❌ Errore nel recuperare la classifica.")

    @commands.command(name='setlevel')
    @commands.has_permissions(administrator=True)
    async def set_level(self, ctx, user: discord.Member, level: int):
        """Imposta il livello di un utente (solo admin)"""
        if level < 1:
            await ctx.send("❌ Il livello deve essere almeno 1!")
            return
            
        required_xp = self.get_required_xp(level)
        
        try:
            async with aiosqlite.connect('database.db') as db:
                await db.execute(
                    'INSERT OR REPLACE INTO levels (user_id, guild_id, xp, level, messages) VALUES (?, ?, ?, ?, ?)',
                    (user.id, ctx.guild.id, required_xp, level, 0)
                )
                await db.commit()
                
            await self.assign_level_roles(user, level, ctx.guild)
            await ctx.send(f"✅ Impostato livello **{level}** per {user.mention} ({required_xp:,} XP)")
            
        except Exception as e:
            print(f"❌ Errore setlevel: {e}")
            await ctx.send("❌ Errore nell'impostare il livello.")

    @commands.command(name='update_lb')
    @commands.has_permissions(administrator=True)
    async def update_leaderboard_command(self, ctx):
        """Aggiorna manualmente la leaderboard (solo admin)"""
        await ctx.message.delete()
        try:
            if self.LEVEL_CHANNEL_ID == 0:
                await ctx.send("❌ Canale leaderboard non configurato!", delete_after=5)
                return
                
            channel = ctx.guild.get_channel(self.LEVEL_CHANNEL_ID)
            if channel:
                await self.send_or_update_leaderboard(channel)
                await ctx.send("✅ Leaderboard aggiornata manualmente!", delete_after=5)
            else:
                await ctx.send("❌ Canale leaderboard non trovato!", delete_after=5)
                
        except Exception as e:
            print(f"❌ Errore aggiornamento manuale leaderboard: {e}")
            await ctx.send("❌ Errore nell'aggiornare la leaderboard!", delete_after=5)

    @commands.command(name='set_leaderboard_channel')
    @commands.has_permissions(administrator=True)
    async def set_leaderboard_channel(self, ctx, channel: discord.TextChannel = None):
        """Imposta il canale per la leaderboard (solo admin)"""
        if channel is None:
            channel = ctx.channel
            
        self.LEVEL_CHANNEL_ID = channel.id
        await ctx.send(f"✅ Canale leaderboard impostato su {channel.mention}", delete_after=10)
        
        await self.update_leaderboard_now()

async def setup(bot):
    await bot.add_cog(Leveling(bot))
