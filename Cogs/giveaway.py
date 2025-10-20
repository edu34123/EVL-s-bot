import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiosqlite
import asyncio
import random
from datetime import datetime, timedelta
import re

class GiveawaySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def init_db(self):
        """Inizializza la tabella giveaway nel database"""
        async with aiosqlite.connect('database.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS giveaways (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    prize TEXT,
                    winners INTEGER,
                    end_time TIMESTAMP,
                    hosted_by INTEGER,
                    requirements TEXT,
                    ended INTEGER DEFAULT 0
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS giveaway_entries (
                    giveaway_id INTEGER,
                    user_id INTEGER,
                    entry_time TIMESTAMP,
                    PRIMARY KEY (giveaway_id, user_id),
                    FOREIGN KEY (giveaway_id) REFERENCES giveaways (id)
                )
            ''')
            await db.commit()
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Avvia il task di controllo giveaway quando il bot è pronto"""
        await self.init_db()
        self.check_giveaways.start()
        print("✅ Sistema Giveaway pronto!")
    
    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        """Controlla i giveaway scaduti ogni 30 secondi"""
        try:
            async with aiosqlite.connect('database.db') as db:
                async with db.execute('''
                    SELECT * FROM giveaways 
                    WHERE ended = 0 AND end_time <= datetime('now')
                ''') as cursor:
                    expired_giveaways = await cursor.fetchall()
                
                for giveaway in expired_giveaways:
                    await self.end_giveaway(giveaway)
                    
        except Exception as e:
            print(f"❌ Errore controllo giveaway: {e}")
    
    async def end_giveaway(self, giveaway):
        """Conclude un giveaway e seleziona i vincitori"""
        giveaway_id, guild_id, channel_id, message_id, prize, winners, end_time, hosted_by, requirements, ended = giveaway
        
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return
            
            # Ottieni tutti i partecipanti
            async with aiosqlite.connect('database.db') as db:
                async with db.execute('''
                    SELECT user_id FROM giveaway_entries WHERE giveaway_id = ?
                ''', (giveaway_id,)) as cursor:
                    entries = await cursor.fetchall()
            
            participants = [entry[0] for entry in entries]
            
            if not participants:
                # Nessun partecipante
                embed = discord.Embed(
                    title="🎉 Giveaway Concluso",
                    description=f"**Premio:** {prize}",
                    color=0xff0000
                )
                embed.add_field(
                    name="❌ Risultato",
                    value="Nessuno ha partecipato al giveaway!",
                    inline=False
                )
                embed.set_footer(text="Giveaway concluso")
                
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(embed=embed, view=None)
                except:
                    await channel.send(embed=embed)
                
            else:
                # Seleziona i vincitori
                if len(participants) < winners:
                    winners = len(participants)
                
                winners_list = random.sample(participants, winners)
                winners_mentions = [f"<@{winner}>" for winner in winners_list]
                
                # Aggiorna il database
                async with aiosqlite.connect('database.db') as db:
                    await db.execute('UPDATE giveaways SET ended = 1 WHERE id = ?', (giveaway_id,))
                    await db.commit()
                
                # Crea l'embed di conclusione
                embed = discord.Embed(
                    title="🎉 Giveaway Concluso!",
                    description=f"**Premio:** {prize}",
                    color=0x00ff00
                )
                embed.add_field(
                    name="🏆 Vincitori",
                    value=", ".join(winners_mentions) if winners_mentions else "Nessun vincitore",
                    inline=False
                )
                embed.add_field(
                    name="👥 Partecipanti",
                    value=f"{len(participants)} partecipanti",
                    inline=True
                )
                embed.add_field(
                    name="🎯 Vincitori selezionati",
                    value=f"{winners}",
                    inline=True
                )
                embed.set_footer(text="Congratulazioni ai vincitori! 🎊")
                
                # Modifica il messaggio originale
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(embed=embed, view=None)
                except:
                    await channel.send(embed=embed)
                
                # Mention dei vincitori
                if winners_mentions:
                    winners_message = f"🎉 **Congratulazioni** {', '.join(winners_mentions)}! Avete vinto **{prize}**!"
                    await channel.send(winners_message)
            
        except Exception as e:
            print(f"❌ Errore conclusione giveaway {giveaway_id}: {e}")
    
    @app_commands.command(name="giveaway", description="Crea un giveaway")
    @app_commands.describe(
        duration="Durata del giveaway (es: 1h, 30m, 2d)",
        winners="Numero di vincitori",
        prize="Premio del giveaway",
        requirements="Requisiti per partecipare (opzionale)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def giveaway(self, interaction: discord.Interaction, duration: str, winners: int, prize: str, requirements: str = "Nessuno"):
        """Crea un nuovo giveaway"""
        await self.init_db()
        
        try:
            # Converti la durata in minuti
            duration_minutes = self.parse_duration(duration)
            if duration_minutes is None:
                await interaction.response.send_message(
                    "❌ Formato durata non valido! Usa: `1h`, `30m`, `2d`, ecc.",
                    ephemeral=True
                )
                return
            
            if winners < 1:
                await interaction.response.send_message("❌ Il numero di vincitori deve essere almeno 1!", ephemeral=True)
                return
            
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Crea l'embed del giveaway
            embed = discord.Embed(
                title="🎉 **GIVEAWAY** 🎉",
                description=f"**Premio:** {prize}",
                color=0x00ff00,
                timestamp=end_time
            )
            
            embed.add_field(
                name="🏆 Vincitori",
                value=f"**{winners}** vincitore{'i' if winners > 1 else ''}",
                inline=True
            )
            
            embed.add_field(
                name="⏰ Termina",
                value=f"<t:{int(end_time.timestamp())}:R>",
                inline=True
            )
            
            embed.add_field(
                name="📋 Requisiti",
                value=requirements,
                inline=False
            )
            
            embed.add_field(
                name="👤 Hosted By",
                value=interaction.user.mention,
                inline=True
            )
            
            embed.add_field(
                name="🎯 Partecipanti",
                value="0",
                inline=True
            )
            
            embed.set_footer(text="Clicca il pulsante qui sotto per partecipare!")
            
            # Crea la view con il pulsante
            view = GiveawayView()
            
            # Invia il messaggio
            message = await interaction.channel.send(embed=embed, view=view)
            
            # Salva nel database
            async with aiosqlite.connect('database.db') as db:
                await db.execute('''
                    INSERT INTO giveaways (guild_id, channel_id, message_id, prize, winners, end_time, hosted_by, requirements)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (interaction.guild.id, interaction.channel.id, message.id, prize, winners, end_time.isoformat(), interaction.user.id, requirements))
                await db.commit()
            
            await interaction.response.send_message(f"✅ Giveaway creato con successo! [Vai al giveaway]({message.jump_url})", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    @app_commands.command(name="greroll", description="Riseleziona i vincitori per un giveaway")
    @app_commands.describe(
        message_id="ID del messaggio del giveaway",
        winners="Numero di nuovi vincitori (opzionale)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def reroll(self, interaction: discord.Interaction, message_id: str, winners: int = None):
        """Riseleziona i vincitori per un giveaway"""
        await self.init_db()
        
        try:
            message_id = int(message_id)
            message = await interaction.channel.fetch_message(message_id)
            
            async with aiosqlite.connect('database.db') as db:
                # Trova il giveaway
                async with db.execute('SELECT * FROM giveaways WHERE message_id = ? AND guild_id = ?', 
                                    (message_id, interaction.guild.id)) as cursor:
                    giveaway = await cursor.fetchone()
                
                if not giveaway:
                    await interaction.response.send_message("❌ Giveaway non trovato!", ephemeral=True)
                    return
                
                giveaway_id, guild_id, channel_id, message_id, prize, original_winners, end_time, hosted_by, requirements, ended = giveaway
                
                if not ended:
                    await interaction.response.send_message("❌ Questo giveaway non è ancora concluso!", ephemeral=True)
                    return
                
                # Usa il numero di vincitori originale se non specificato
                if winners is None:
                    winners = original_winners
                
                # Ottieni i partecipanti
                async with db.execute('SELECT user_id FROM giveaway_entries WHERE giveaway_id = ?', 
                                    (giveaway_id,)) as cursor:
                    entries = await cursor.fetchall()
                
                participants = [entry[0] for entry in entries]
                
                if not participants:
                    await interaction.response.send_message("❌ Nessun partecipante per questo giveaway!", ephemeral=True)
                    return
                
                if len(participants) < winners:
                    winners = len(participants)
                
                # Seleziona nuovi vincitori
                new_winners = random.sample(participants, winners)
                winners_mentions = [f"<@{winner}>" for winner in new_winners]
                
                # Invia il messaggio di reroll
                reroll_embed = discord.Embed(
                    title="🔄 Reroll Giveaway",
                    description=f"**Premio:** {prize}",
                    color=0xffff00
                )
                reroll_embed.add_field(
                    name="🏆 Nuovi Vincitori",
                    value=", ".join(winners_mentions),
                    inline=False
                )
                reroll_embed.set_footer(text=f"Reroll eseguito da {interaction.user.display_name}")
                
                await interaction.channel.send(embed=reroll_embed)
                await interaction.response.send_message("✅ Reroll completato!", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ ID messaggio non valido!", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ Messaggio non trovato!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    @app_commands.command(name="giveaway_list", description="Mostra i giveaway attivi")
    async def giveaway_list(self, interaction: discord.Interaction):
        """Mostra la lista dei giveaway attivi"""
        await self.init_db()
        
        try:
            async with aiosqlite.connect('database.db') as db:
                async with db.execute('''
                    SELECT * FROM giveaways 
                    WHERE guild_id = ? AND ended = 0 
                    ORDER BY end_time ASC
                ''', (interaction.guild.id,)) as cursor:
                    active_giveaways = await cursor.fetchall()
            
            if not active_giveaways:
                embed = discord.Embed(
                    title="🎉 Giveaway Attivi",
                    description="Nessun giveaway attivo al momento!",
                    color=0xffff00
                )
                await interaction.response.send_message(embed=embed)
                return
            
            embed = discord.Embed(
                title="🎉 Giveaway Attivi",
                color=0x00ff00
            )
            
            for giveaway in active_giveaways:
                giveaway_id, guild_id, channel_id, message_id, prize, winners, end_time, hosted_by, requirements, ended = giveaway
                
                channel = interaction.guild.get_channel(channel_id)
                channel_name = f"#{channel.name}" if channel else "Canale sconosciuto"
                
                end_time_dt = datetime.fromisoformat(end_time)
                time_left = f"<t:{int(end_time_dt.timestamp())}:R>"
                
                embed.add_field(
                    name=f"🎁 {prize}",
                    value=f"**Vincitori:** {winners}\n**Termina:** {time_left}\n**Canale:** {channel_name}\n[Vai al giveaway](https://discord.com/channels/{guild_id}/{channel_id}/{message_id})",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)
    
    def parse_duration(self, duration: str) -> int:
        """Converte una stringa di durata in minuti"""
        match = re.match(r'^(\d+)([hmd])$', duration.lower())
        if not match:
            return None
        
        amount = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'm':
            return amount
        elif unit == 'h':
            return amount * 60
        elif unit == 'd':
            return amount * 24 * 60
        else:
            return None

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎉 Partecipa", style=discord.ButtonStyle.success, custom_id="giveaway_join")
    async def join_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestisce la partecipazione al giveaway"""
        try:
            # Trova il giveaway nel database
            async with aiosqlite.connect('database.db') as db:
                async with db.execute('SELECT * FROM giveaways WHERE message_id = ? AND ended = 0', 
                                    (interaction.message.id,)) as cursor:
                    giveaway = await cursor.fetchone()
                
                if not giveaway:
                    await interaction.response.send_message("❌ Giveaway non trovato o già concluso!", ephemeral=True)
                    return
                
                giveaway_id = giveaway[0]
                
                # Controlla se l'utente ha già partecipato
                async with db.execute('SELECT * FROM giveaway_entries WHERE giveaway_id = ? AND user_id = ?', 
                                    (giveaway_id, interaction.user.id)) as cursor:
                    existing_entry = await cursor.fetchone()
                
                if existing_entry:
                    await interaction.response.send_message("❌ Hai già partecipato a questo giveaway!", ephemeral=True)
                    return
                
                # Aggiungi l'utente al giveaway
                await db.execute('INSERT INTO giveaway_entries (giveaway_id, user_id, entry_time) VALUES (?, ?, ?)',
                               (giveaway_id, interaction.user.id, datetime.now().isoformat()))
                await db.commit()
                
                # Conta i partecipanti totali
                async with db.execute('SELECT COUNT(*) FROM giveaway_entries WHERE giveaway_id = ?', 
                                    (giveaway_id,)) as cursor:
                    participant_count = await cursor.fetchone()
                
                # Aggiorna l'embed
                embed = interaction.message.embeds[0]
                for i, field in enumerate(embed.fields):
                    if field.name == "🎯 Partecipanti":
                        embed.set_field_at(i, name="🎯 Partecipanti", value=str(participant_count[0]), inline=True)
                        break
                
                await interaction.message.edit(embed=embed)
                await interaction.response.send_message("✅ Partecipazione registrata! Buona fortuna! 🍀", ephemeral=True)
                
        except Exception as e:
            await interaction.response.send_message("❌ Errore durante la partecipazione!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GiveawaySystem(bot))
    # Aggiungi la view persistente
    bot.add_view(GiveawayView())
