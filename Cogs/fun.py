import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
import random
import aiohttp  # type: ignore

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="meme", description="Mostra un meme casuale")
    async def meme(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as response:
                data = await response.json()
                
                embed = discord.Embed(title=data['title'], color=0x00ff00)
                embed.set_image(url=data['url'])
                embed.set_footer(text=f"r/{data['subreddit']} | 👍 {data['ups']}")
                
                await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="8ball", description="Fai una domanda alla palla magica")
    @app_commands.describe(question="La tua domanda")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
        "Certainly!"
        "Without a doubt!"
        "Yes, definitely!"
        "Most likely!"
        "The prospects are good!"
        "Ask later..."
        "Better not to tell you now..."
        "Don't count on it!"
        "My answer is no!"
        "Very doubtful!"
        ]
        
        embed = discord.Embed(title="🎱 La Palla Magica", color=0x9B59B6)
        embed.add_field(name="Domanda", value=question, inline=False)
        embed.add_field(name="Risposta", value=random.choice(responses), inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))