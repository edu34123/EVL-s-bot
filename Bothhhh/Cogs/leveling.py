import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
import aiosqlite # type: ignore
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
                'INSERT OR REPLACE INTO levels (user_id, guild_id, xp, level) VALUES (?, ?, COALESCE((SELECT xp FROM levels WHERE user_id = ?), 0) + ?, COALESCE((SELECT level FROM levels WHERE user_id = ?), 1))',
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
                
                embed = discord.Embed(title=f"📊 Livello di {target_user}", color=0x00ff00)
                embed.add_field(name="Livello", value=level, inline=True)
                embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
                embed.set_thumbnail(url=target_user.avatar.url)
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Utente non trovato nel database!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leveling(bot))