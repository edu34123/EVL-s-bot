import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import random

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Aggiungi XP casuale
        xp_to_add = random.randint(5, 15)
        
        async with aiosqlite.connect('database.db') as db:
            await db.execute(
                '''INSERT OR REPLACE INTO levels (user_id, guild_id, xp, level) 
                   VALUES (?, ?, COALESCE((SELECT xp FROM levels WHERE user_id = ?), 0) + ?, 
                   COALESCE((SELECT level FROM levels WHERE user_id = ?), 1))''',
                (message.author.id, message.guild.id, message.author.id, xp_to_add, message.author.id)
            )
            await db.commit()
            
            # Controlla livello up
            cursor = await db.execute(
                'SELECT xp, level FROM levels WHERE user_id = ?',
                (message.author.id,)
            )
            result = await cursor.fetchone()
            
            if result:
                xp, level = result
                xp_needed = level * 100
                
                if xp >= xp_needed:
                    new_level = level + 1
                    await db.execute(
                        'UPDATE levels SET level = ?, xp = ? WHERE user_id = ?',
                        (new_level, 0, message.author.id)
                    )
                    await db.commit()
                    
                    embed = discord.Embed(
                        title="🎉 Level Up!",
                        description=f"{message.author.mention} è salito al livello **{new_level}**!",
                        color=0x00ff00
                    )
                    await message.channel.send(embed=embed)
    
    @app_commands.command(name="level", description="Controlla il tuo livello")
    async def level(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute(
                'SELECT xp, level FROM levels WHERE user_id = ?',
                (target_user.id,)
            )
            result = await cursor.fetchone()
            
            if result:
                xp, level = result
                xp_needed = level * 100
                progress = min((xp / xp_needed) * 100, 100)
                
                # Crea una barra di progresso
                bars = 10
                filled_bars = int((xp / xp_needed) * bars)
                progress_bar = "█" * filled_bars + "░" * (bars - filled_bars)
                
                embed = discord.Embed(title=f"📊 Livello di {target_user.display_name}", color=0x00ff00)
                embed.add_field(name="Livello", value=f"**{level}**", inline=True)
                embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
                embed.add_field(name="Progresso", value=f"{progress_bar} {progress:.1f}%", inline=False)
                embed.set_thumbnail(url=target_user.display_avatar.url)
                
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(title="📊 Livello", description="Non hai ancora esperienza! Scrivi qualche messaggio per iniziare.", color=0xffff00)
                await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Classifica dei livelli")
    async def leaderboard(self, interaction: discord.Interaction):
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute(
                'SELECT user_id, level, xp FROM levels WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT 10',
                (interaction.guild.id,)
            )
            results = await cursor.fetchall()
            
            if not results:
                await interaction.response.send_message("Nessun dato nella classifica ancora!", ephemeral=True)
                return
            
            embed = discord.Embed(title="🏆 Classifica Livelli", color=0xffd700)
            
            leaderboard_text = ""
            for i, (user_id, level, xp) in enumerate(results, 1):
                user = interaction.guild.get_member(user_id)
                username = user.display_name if user else f"Utente {user_id}"
                
                medal = ""
                if i == 1: medal = "🥇"
                elif i == 2: medal = "🥈" 
                elif i == 3: medal = "🥉"
                
                leaderboard_text += f"{medal} **{i}.** {username} - Livello {level} ({xp} XP)\n"
            
            embed.description = leaderboard_text
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Leveling(bot))
