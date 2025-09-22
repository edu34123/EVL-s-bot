import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
import aiosqlite # type: ignore
from config import INVITE_ROLES  # Importa dalla config # type: ignore

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}
    
    # ... resto del codice invariato ...
    
    async def assign_invite_roles(self, member, invites_count):
        for threshold, role_id in INVITE_ROLES.items():  # Usa il dizionario dalla config
            role = member.guild.get_role(role_id)
            if role and invites_count >= threshold:
                if role not in member.roles:
                    await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))