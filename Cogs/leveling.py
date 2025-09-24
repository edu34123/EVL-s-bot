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
            4: 600,      # Livello 4: 600 XP
            5: 1000,     # Livello 5: 1,000 XP
            6: 1500,     # Livello 6: 1,500 XP
            7: 2100,     # Livello 7: 2,100 XP
            8: 2800,     # Livello 8: 2,800 XP
            9: 3600,     # Livello 9: 3,600 XP
            10: 4500,    # Livello 10: 4,500 XP
            11: 5500,    # Livello 11: 5,500 XP
            12: 6600,    # Livello 12: 6,600 XP
            13: 7800,    # Livello 13: 7,800 XP
            14: 9100,    # Livello 14: 9,100 XP
            15: 10500,   # Livello 15: 10,500 XP
            16: 12000,   # Livello 16: 12,000 XP
            17: 13600,   # Livello 17: 13,600 XP
            18: 15300,   # Livello 18: 15,300 XP
            19: 17100,   # Livello 19: 17,100 XP
            20: 19000,   # Livello 20: 19,000 XP
            21: 21000,   # Livello 21: 21,000 XP
            22: 23100,   # Livello 22: 23,100 XP
            23: 25300,   # Livello 23: 25,300 XP
            24: 27600,   # Livello 24: 27,600 XP
            25: 30000,   # Livello 25: 30,000 XP
            26: 32500,   # Livello 26: 32,500 XP
            27: 35100,   # Livello 27: 35,100 XP
            28: 37800,   # Livello 28: 37,800 XP
            29: 40600,   # Livello 29: 40,600 XP
            30: 43500,   # Livello 30: 43,500 XP
            31: 46500,   # Livello 31: 46,500 XP
            32: 49600,   # Livello 32: 49,600 XP
            33: 52800,   # Livello 33: 52,800 XP
            34: 56100,   # Livello 34: 56,100 XP
            35: 59500,   # Livello 35: 59,500 XP
            36: 63000,   # Livello 36: 63,000 XP
            37: 66600,   # Livello 37: 66,600 XP
            38: 70300,   # Livello 38: 70,300 XP
            39: 74100,   # Livello 39: 74,100 XP
            40: 78000,   # Livello 40: 78,000 XP
            41: 82000,   # Livello 41: 82,000 XP
            42: 86100,   # Livello 42: 86,100 XP
            43: 90300,   # Livello 43: 90,300 XP
            44: 94600,   # Livello 44: 94,600 XP
            45: 99000,   # Livello 45: 99,000 XP
            46: 103500,  # Livello 46: 103,500 XP
            47: 108100,  # Livello 47: 108,100 XP
            48: 112800,  # Livello 48: 112,800 XP
            49: 117600,  # Livello 49: 117,600 XP
            50: 122500,  # Livello 50: 122,500 XP
            51: 127500,  # Livello 51: 127,500 XP
            52: 132600,  # Livello 52: 132,600 XP
            53: 137800,  # Livello 53: 137,800 XP
            54: 143100,  # Livello 54: 143,100 XP
            55: 148500,  # Livello 55: 148,500 XP
            56: 154000,  # Livello 56: 154,000 XP
            57: 159600,  # Livello 57: 159,600 XP
            58: 165300,  # Livello 58: 165,300 XP
            59: 171100,  # Livello 59: 171,100 XP
            60: 177000,  # Livello 60: 177,000 XP
            61: 183000,  # Livello 61: 183,000 XP
            62: 189100,  # Livello 62: 189,100 XP
            63: 195300,  # Livello 63: 195,300 XP
            64: 201600,  # Livello 64: 201,600 XP
            65: 208000,  # Livello 65: 208,000 XP
            66: 214500,  # Livello 66: 214,500 XP
            67: 221100,  # Livello 67: 221,100 XP
            68: 227800,  # Livello 68: 227,800 XP
            69: 234600,  # Livello 69: 234,600 XP
            70: 241500,  # Livello 70: 241,500 XP
            71: 248500,  # Livello 71: 248,500 XP
            72: 255600,  # Livello 72: 255,600 XP
            73: 262800,  # Livello 73: 262,800 XP
            74: 270100,  # Livello 74: 270,100 XP
            75: 277500,  # Livello 75: 277,500 XP
            76: 285000,  # Livello 76: 285,000 XP
            77: 292600,  # Livello 77: 292,600 XP
            78: 300300,  # Livello 78: 300,300 XP
            79: 308100,  # Livello 79: 308,100 XP
            80: 316000,  # Livello 80: 316,000 XP
            81: 324000,  # Livello 81: 324,000 XP
            82: 332100,  # Livello 82: 332,100 XP
            83: 340300,  # Livello 83: 340,300 XP
            84: 348600,  # Livello 84: 348,600 XP
            85: 357000,  # Livello 85: 357,000 XP
            86: 365500,  # Livello 86: 365,500 XP
            87: 374100,  # Livello 87: 374,100 XP
            88: 382800,  # Livello 88: 382,800 XP
            89: 391600,  # Livello 89: 391,600 XP
            90: 400500,  # Livello 90: 400,500 XP
            91: 409500,  # Livello 91: 409,500 XP
            92: 418600,  # Livello 92: 418,600 XP
            93: 427800,  # Livello 93: 427,800 XP
            94: 437100,  # Livello 94: 437,100 XP
            95: 446500,  # Livello 95: 446,500 XP
            96: 456000,  # Livello 96: 456,000 XP
            97: 465600,  # Livello 97: 465,600 XP
            98: 475300,  # Livello 98: 475,300 XP
            99: 485100,  # Livello 99: 485,100 XP
            100: 495000, # Livello 100: 495,000 XP
            # Livelli sopra 100 con incrementi maggiori
            101: 510000,
            102: 525000,
            103: 540000,
            104: 555000,
            105: 570000,
            106: 585000,
            107: 600000,
            108: 615000,
            109: 630000,
            110: 645000,
            115: 720000,
            120: 800000,
            125: 885000,
            130: 975000,
            135: 1070000,
            140: 1170000,
            145: 1275000,
            150: 1385000,
            155: 1500000,
            160: 1620000,
            165: 1745000,
            170: 1875000,
            175: 2010000,
            180: 2150000,
            185: 2295000,
            190: 2445000,
            195: 2600000,
            200: 2760000,
            205: 2930000,
            210: 3105000,
            215: 3285000,
            220: 3470000,
            225: 3660000,
            230: 3855000,
            235: 4055000,
            240: 4260000,
            245: 4470000,
            250: 4685000,
            255: 4905000,
            260: 5130000,
            265: 5360000,
            270: 5595000,
            275: 5835000,
            280: 6080000,
            285: 6330000,
            290: 6585000,
            295: 6845000,
            300: 7110000  # Livello 300: 7,110,000 XP (oltre i 6M richiesti)
        }
        
        # Ruoli per ogni livello
        self.level_roles = {
            5: int(os.getenv('LEVEL_5_ROLE', '1392732183671738471')),
            10: int(os.getenv('LEVEL_10_ROLE', '1392732172460228618')),
            15: int(os.getenv('LEVEL_15_ROLE', '1392732221412216852')),
            20: int(os.getenv('LEVEL_20_ROLE', '1392732221495967745')),
            30: int(os.getenv('LEVEL_30_ROLE', '1392732227716255885')),
            40: int(os.getenv('LEVEL_40_ROLE', '1392732228186013877')),
            50: int(os.getenv('LEVEL_50_ROLE', '1392732233382625400')),
            75: int(os.getenv('LEVEL_75_ROLE', '1392732233961312377')),
            100: int(os.getenv('LEVEL_100_ROLE', '1392732244040351909')),
            150: int(os.getenv('LEVEL_150_ROLE', '0')),
            200: int(os.getenv('LEVEL_200_ROLE', '1392732244858114089')),
            250: int(os.getenv('LEVEL_250_ROLE', '1419373735282086051')),
            300: int(os.getenv('LEVEL_300_ROLE', '1419373736728985772'))
        }

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
                    await self.send_or_update_leaderboard(channel)
                    break
        except Exception as e:
            print(f"❌ Errore aggiornamento leaderboard automatico: {e}")

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        """Aspetta che il bot sia pronto prima di iniziare il task"""
        await self.bot.wait_until_ready()

    async def send_or_update_leaderboard(self, channel):
        """Invia o aggiorna la leaderboard nel canale"""
        try:
            embed = await self.create_leaderboard_embed(channel.guild)
            
            if self.leaderboard_message_id:
                try:
                    message = await channel.fetch_message(self.leaderboard_message_id)
                    await message.edit(embed=embed)
                    print("✅ Leaderboard aggiornata")
                    return
                except:
                    self.leaderboard_message_id = None
            
            async for message in channel.history(limit=10):
                if message.author == self.bot.user and message.embeds:
                    for embed_msg in message.embeds:
                        if embed_msg.title and "Classifica Livelli" in embed_msg.title:
                            self.leaderboard_message_id = message.id
                            await message.edit(embed=embed)
                            print("✅ Leaderboard aggiornata (messaggio esistente)")
                            return
            
            message = await channel.send(embed=embed)
            self.leaderboard_message_id = message.id
            print("✅ Leaderboard creata")
            
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
