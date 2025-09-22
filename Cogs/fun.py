import discord
from discord import app_commands
from discord.ext import commands
import random
import aiohttp
import json

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="meme", description="Mostra un meme casuale")
    async def meme(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title=data['title'], color=0x00ff00)
                    embed.set_image(url=data['url'])
                    embed.set_footer(text=f"r/{data['subreddit']} | 👍 {data['ups']}")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("❌ Impossibile caricare il meme!", ephemeral=True)
    
    @app_commands.command(name="8ball", description="Fai una domanda alla palla magica")
    @app_commands.describe(question="La tua domanda")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "Certamente! 🎱", "Senza dubbio! 🎱", "Sì, definitivamente! 🎱",
            "Molto probabilmente! 🎱", "Le prospettive sono buone! 🎱",
            "Chiedi più tardi... 🎱", "Meglio non dirtelo ora... 🎱",
            "Non ci contare! 🎱", "La mia risposta è no! 🎱", "Molto dubbioso! 🎱"
        ]
        
        embed = discord.Embed(title="🎱 La Palla Magica", color=0x9B59B6)
        embed.add_field(name="Domanda", value=question, inline=False)
        embed.add_field(name="Risposta", value=random.choice(responses), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="cat", description="Mostra un gatto casuale")
    async def cat(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title="🐱 Ecco un gatto per te!", color=0xff9900)
                    embed.set_image(url=data[0]['url'])
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("❌ Impossibile caricare il gatto!", ephemeral=True)
    
    @app_commands.command(name="dado", description="Lancia un dado")
    @app_commands.describe(facce="Numero di facce del dado (default: 6)")
    async def dice(self, interaction: discord.Interaction, facce: int = 6):
        if facce < 2:
            await interaction.response.send_message("Il dado deve avere almeno 2 facce!", ephemeral=True)
            return
        
        risultato = random.randint(1, facce)
        embed = discord.Embed(title="🎲 Lancio del Dado", color=0x3498db)
        embed.add_field(name="Risultato", value=f"**{risultato}** su {facce} facce", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quote", description="Mostra una citazione inspirazionale")
    async def quote(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.quotable.io/random') as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title="💫 Citazione Inspirazionale", color=0x9B59B6)
                    embed.add_field(name="Citazione", value=data['content'], inline=False)
                    embed.add_field(name="Autore", value=data['author'], inline=False)
                    await interaction.response.send_message(embed=embed)
                else:
                    embed = discord.Embed(title="💫 Citazione Inspirazionale", color=0x9B59B6)
                    embed.add_field(name="Citazione", value="La vita è ciò che ti succede mentre sei impegnato a fare altri piani.", inline=False)
                    embed.add_field(name="Autore", value="John Lennon", inline=False)
                    await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
