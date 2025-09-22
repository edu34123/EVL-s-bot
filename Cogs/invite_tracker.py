import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except:
                pass
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        invites_before = self.invites.get(guild.id, [])
        invites_after = await guild.invites()
        
        for invite in invites_before:
            for new_invite in invites_after:
                if invite.code == new_invite.code and invite.uses < new_invite.uses:
                    inviter = new_invite.inviter
                    
                    if inviter:
                        async with aiosqlite.connect('database.db') as db:
                            await db.execute(
                                '''INSERT OR REPLACE INTO invites (user_id, guild_id, invites_count) 
                                   VALUES (?, ?, COALESCE((SELECT invites_count FROM invites WHERE user_id = ?), 0) + 1)''',
                                (inviter.id, guild.id, inviter.id)
                            )
                            await db.commit()
                            
                            cursor = await db.execute(
                                'SELECT invites_count FROM invites WHERE user_id = ?',
                                (inviter.id,)
                            )
                            result = await cursor.fetchone()
                            
                            if result:
                                invites_count = result[0]
                                await self.assign_invite_roles(inviter, invites_count)
        
        self.invites[guild.id] = invites_after
    
    async def assign_invite_roles(self, member, invites_count):
        from main import INVITE_ROLES
        
        for threshold, role_id in INVITE_ROLES.items():
            role = member.guild.get_role(role_id)
            if role and invites_count >= threshold:
                if role not in member.roles:
                    # Rimuovi altri ruoli inviti
                    for other_role_id in INVITE_ROLES.values():
                        other_role = member.guild.get_role(other_role_id)
                        if other_role and other_role in member.roles:
                            await member.remove_roles(other_role)
                    
                    await member.add_roles(role)
                    
                    embed = discord.Embed(
                        title="🎉 Nuovo Ruolo Inviti!",
                        description=f"{member.mention} ha ottenuto il ruolo {role.mention} per aver invitato {invites_count} persone!",
                        color=0x00ff00
                    )
                    channel = member.guild.system_channel
                    if channel:
                        await channel.send(embed=embed)
    
    @app_commands.command(name="invites", description="Controlla i tuoi inviti")
    async def invites(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        
        async with aiosqlite.connect('database.db') as db:
            cursor = await db.execute(
                'SELECT invites_count FROM invites WHERE user_id = ?',
                (target_user.id,)
            )
            result = await cursor.fetchone()
            
            invites_count = result[0] if result else 0
            
            from main import INVITE_ROLES
            next_roles = []
            for threshold, role_id in INVITE_ROLES.items():
                role = interaction.guild.get_role(role_id)
                if role and invites_count < threshold:
                    needed = threshold - invites_count
                    next_roles.append(f"{role.mention} - {needed} inviti rimanenti")
                    if len(next_roles) >= 3:  # Mostra solo i prossimi 3 ruoli
                        break
            
            embed = discord.Embed(title=f"📨 Inviti di {target_user.display_name}", color=0x00ff00)
            embed.add_field(name="Inviti Totali", value=f"**{invites_count}**", inline=False)
            
            if next_roles:
                embed.add_field(name="Prossimi Ruoli", value="\n".join(next_roles), inline=False)
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
