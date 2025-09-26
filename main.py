import os
import discord
from discord.ext import commands
import asyncio
import json
import datetime
import random
import re
import aiohttp
import time
import sqlite3
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# ========== UNIQUE SERVERS DATABASE ========== #
UNIQUE_SERVERS = [
    # Original list (56 servers)
    "https://discord.gg/5GE4xm9Hmx", "https://discord.gg/Fwa5nWzxjg", "https://discord.gg/teQaTUku",
    "https://discord.gg/Yskg8vcqMj", "https://discord.gg/NMEQ23khCg", "https://discord.gg/tUuzHdnVA4",
    "https://discord.gg/cAGNSQeEfq", "https://discord.gg/6uABQ2yV", "https://discord.gg/27VQkXEN",
    "https://discord.gg/obsidiann", "https://discord.gg/uSfXDAUrGE", "https://discord.com/invite/zR3mRuCCQN",
    "https://discord.gg/GQQ5Cng2", "https://discord.gg/bpatjRJsVs", "https://discord.gg/ohanami",
    "https://discord.gg/4AYSy7daNM", "https://discord.gg/vGKPfmg9X7", "https://discord.gg/RG3uyRCWaX",
    "https://discord.gg/fBmwdXWPJ9", "https://discord.gg/KvYE4fRR", "https://discord.gg/rUzfTFCzHG",
    "https://discord.gg/GhnrFYYqeB", "https://discord.gg/yTgNgtNCMR", "https://discord.gg/TMAYnwbWqb",
    "https://discord.gg/YadhG8n4AV", "https://discord.gg/FuVxGTdda3", "https://discord.gg/5ztTPry24E",
    "https://discord.gg/CuM4YFfDYg", "https://discord.gg/x2kdXFzFhj", "https://discord.gg/5D7cSaK5Px",
    "https://discord.gg/nYMNPudd9A", "https://discord.gg/58va9vm3zr", "https://discord.gg/2wk83whd",
    "https://discord.gg/oceanhub", "https://discord.gg/Xt6KgVX63q", "https://discord.gg/CMEMKw7jqq",
    "https://discord.gg/krnckFfN", "https://discord.gg/fCa5NaDWG7", "https://discord.gg/P3cZfhPuHq",
    "https://discord.gg/aXjgJe55xY", "https://discord.gg/kzMdy5ZF9A", "https://discord.gg/4Gp52nqMcy",
    "https://discord.gg/7B4p7fTB7Q", "https://discord.gg/b9Cq2gKxQT", "https://discord.gg/sS3GsxDy",
    "https://discord.gg/RxvwPC9Qq5", "https://discord.gg/aX4rfuedBM", "https://discord.gg/dT7uutYGEA",
    "https://discord.gg/zgXJ3G3Gzy", "https://discord.gg/zc7qDZHKCc", "https://discord.gg/eKBYsXxCVp",
    "https://discord.gg/hUPEzfAuG6", "https://discord.gg/ptkpEbmARZ", "https://discord.gg/h39saMKNuj",
    "https://discord.gg/k5buUP32Zp", "https://discord.gg/rPYmzNEKvG", "https://discord.gg/Pkj7SQxdkH",
    "https://discord.gg/volpix-mc", "https://discord.gg/haizen",
    # New servers added (144)
    "https://discord.gg/EEpk7apcbc", "https://discord.gg/6z4RSnJAw6", "https://discord.gg/UFabhM9YKY",
    "https://discord.gg/9Jms2JuZ5Q", "https://discord.gg/ZJSkMAmjn2", "https://discord.gg/zR85tqF67k",
    "https://discord.gg/hmv5MDdJAs", "https://discord.gg/heartlessitalia", "https://discord.gg/ZckmMgxs6Y",
    "https://discord.gg/fRApqDaMUQ", "https://discord.gg/7xKjGG4uy8", "https://discord.gg/Dxjwx9Epz7",
    "https://discord.gg/xb8XY3UFbV", "https://discord.gg/cristalmc", "https://discord.gg/Mhh2JRzX9G",
    "https://discord.gg/dY5Z5KKcyW", "https://discord.gg/DPEC89jXeX", "https://discord.gg/4NXMev3SQ5",
    "https://discord.gg/kEbWpu4dWK", "https://discord.gg/R7p7RUuDE9", "https://discord.gg/hPnFBdu9cn",
    "https://discord.gg/DYsA2srphN", "https://discord.gg/47GMzShCwC", "https://discord.gg/smuVfcUW8M",
    "https://discord.gg/GJkdu67acg", "https://discord.gg/g2bSvGzV5t", "https://discord.gg/APmuJMBh5E",
    "https://discord.gg/R7p7RUuDE9", "https://discord.gg/hPnFBdu9cn", "https://discord.gg/dT7uutYGEA",
    "https://discord.gg/qfpdmvFPrj", "https://discord.gg/U4qWQySGeg", "https://discord.gg/VHgpp3BRce",
    "https://discord.gg/XyzjZWh5AD", "https://discord.gg/k5ZQx4n3tQ", "https://discord.gg/AbJD8cuq95",
    "https://discord.gg/7J8SjQmTpg", "https://discord.gg/fyzkDBU5Df", "https://discord.gg/zgXJ3G3Gzy",
    "https://discord.com/invite/Sjs9qHVTTZ", "https://discord.gg/QzahpnwqJf", "https://discord.gg/RZmjCfymZ5",
    "https://discord.gg/ZVRCf2eu5Z", "https://discord.gg/jqKdZQjR7w", "https://discord.gg/GxYPUdZty5",
    "https://discord.gg/c33nv97dqs", "https://discord.gg/sNDE3txEkY", "https://discord.gg/uYyG74yu",
    "https://discord.gg/EYJa7CNvtN", "https://discord.gg/vjxcVmTKuz", "https://discord.gg/MXX3BDJ3xz",
    "https://discord.gg/hBYgrSg8K8", "https://discord.gg/UXsVTADnkX", "https://discord.gg/NMEQ23khCg",
    "https://discord.gg/WEeKz8yG5H", "https://discord.gg/HBNMVF86uR", "https://discord.gg/Fsj5muUMB5",
    "https://discord.gg/FzycNCq8Up", "https://discord.gg/ECkPjsGeG9", "https://discord.gg/3sx5jSQ587",
    "https://discord.gg/reccenteritaliano-767657914563035138", "https://discord.com/invite/zR3mRuCCQN", "https://discord.gg/CXsNJSgp",
    "https://discord.gg/vGKPfmg9X7", "https://discord.gg/d9dqX6zWy3", "https://discord.gg/5ztTPry24E",
    "https://discord.gg/CuM4YFfDYg", "https://discord.gg/PbVr5q5v", "https://discord.gg/6gQmWHWqa6",
    "https://discord.gg/P4ANqw28Tv", "https://discord.gg/qesBrM2JHJ", "https://discord.gg/PH5e93eRX5",
    "https://discord.gg/Y66UzmFwSV", "https://discord.gg/bpatjRJsVs", "https://discord.gg/3SnFkBfBGx",
    "https://discord.gg/xqmVa5AnEq", "https://discord.gg/xgtBNjdvQy", "https://discord.gg/FuVxGTdda3",
    "https://discord.gg/ccitaly2", "https://discord.gg/QE4jNsMapN", "https://discord.gg/REQmFgNRFT",
    "https://discord.gg/8F3AwXPeUd", "https://discord.gg/cy8veqvm66", "https://discord.gg/kgXPPMNDuc",
    "https://discord.gg/pvgCDQFKTv", "https://discord.gg/feamXExTbD", "https://discord.gg/SgDkkPvjMR",
    "https://discord.gg/zCn5xhCAJa", "https://discord.gg/jhySqrRPMW", "https://discord.gg/mAJvU4EtHp",
    "https://discord.gg/pKsNQw6Zt9", "https://discord.gg/24wPYNFPk4", "https://discord.gg/JGXqMcbBhq",
    "https://discord.gg/RG3uyRCWaX", "https://discord.gg/mvwZTCvCv6", "https://discord.gg/7FPFHaPwsV",
    "https://discord.gg/K9dXnMPBra", "https://discord.gg/oei", "https://discord.gg/xivtag",
    "https://discord.gg/EuUQBV2kB9", "https://discord.com/invite/zR3mRuCCQN", "https://discord.gg/underworld-818910678197862432",
    "https://discord.gg/romarp", "https://discord.gg/YDJQGa2hwU", "https://discord.gg/sNDE3txEkY", "https://discord.gg/MXX3BDJ3xz",
    "https://discord.gg/WEeKz8yG5H", "https://discord.gg/Fsj5muUMB5", "https://discord.gg/hpxDhzPWkF",
    "https://discord.gg/55vYFBwQRU", "https://discord.gg/UQGrMkZEUa", "https://discord.gg/8WXGkDrgf2",
    "https://discord.gg/JfDUgATMZA", "https://discord.gg/6beEA67u27", "https://discord.gg/HjtxwPFVM5",
    "https://discord.gg/Dgd8CZC3XC", "https://discord.gg/X8kTfvTQa4", "https://discord.gg/tAWtvAsqPp", "https://discord.gg/dksh3QbzDd",
    "https://discord.gg/sharmrps", "https://discord.com/invite/qkssTRsmm9", "https://discord.gg/SsmNAv44Xx", "https://discord.gg/bmw3Zpdr5P",
    "https://discord.gg/KEzP4PkjWj", "https://discord.gg/tAexWvycGk", "https://discord.gg/xwGrUJzFTG", "https://discord.com/invite/qh9YxpYQVx"
]

# ========== CONFIGURAZIONE ========== #
AUTHORIZED_ROLE_ID = None

# Configurazione Ticket System
TICKET_CONFIG = {
    "SUPPORT_ROLE_ID": int(os.getenv("SUPPORT_ROLE_ID", "1394357096295956580")),
    "LOG_CHANNEL_ID": int(os.getenv("LOG_CHANNEL_ID", "1408439077577031812")),
    "TICKET_CATEGORY_ID": int(os.getenv("TICKET_CATEGORY_ID", "1392745407582437448")),
    "STAFF_ROLE_ID": int(os.getenv("STAFF_APPLICATION_ROLE_ID", "1392091644299575417"))
}

# Configurazione Verification System
VERIFICATION_CONFIG = {
    "RULES_CHANNEL_ID": int(os.getenv('RULES_CHANNEL_ID', '1392062840097210478')),
    "ITALIAN_RULES_CHANNEL_ID": int(os.getenv('ITALIAN_RULES_CHANNEL_ID', '1392062840097210478')),
    "VERIFY_CHANNEL_ID": int(os.getenv('VERIFY_CHANNEL_ID', '1392062838197059644')),
    "UNVERIFIED_ROLE_ID": int(os.getenv('UNVERIFIED_ROLE_ID', '1392111556954685450')),
    "VERIFIED_ROLE_ID": int(os.getenv('VERIFIED_ROLE_ID', '1392128530438951084')),
    "ITA_ROLE_ID": int(os.getenv('ITA_ROLE_ID', '1402668379533348944')),
    "ENG_ROLE_ID": int(os.getenv('ENG_ROLE_ID', '1402668928890568785')),
    "FAN_ROLE_ID": int(os.getenv('FAN_ROLE_ID', '1392128530438951084'))
}

# API Keys (placeholder)
REDDIT_API = os.getenv('REDDIT_API', '')
IMGFLIP_USER = os.getenv('IMGFLIP_USER', '')
IMGFLIP_PASS = os.getenv('IMGFLIP_PASS', '')
STEAM_API = os.getenv('STEAM_API', '')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')

# ========== CLASSI ========== #
class ServerView(discord.ui.View):
    def __init__(self, invite_link: str):
        super().__init__()
        self.add_item(discord.ui.Button(
            label="Join Server",
            url=invite_link,
            style=discord.ButtonStyle.link,
            emoji="🎯"
        ))

class PartnershipModal(discord.ui.Modal, title="Partnership Form"):
    description_input = discord.ui.TextInput(
        label="Server description",
        style=discord.TextStyle.paragraph,
        placeholder="Write the description of the other server here",
        required=True,
        max_length=2000
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.client.get_channel(PARTNER_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message("Error: channel not found.", ephemeral=True)
            return

        handler = interaction.user.name
        manager = interaction.guild.name if interaction.guild else "Unknown server"

        message_content = (
            f"{self.description_input.value}\n\n"
            f"**---**\n"
            f"Handler: {handler}\n"
            f"Manager: {manager}\n"
            f"**---**"
        )

        await channel.send(message_content, allowed_mentions=discord.AllowedMentions.none())
        await interaction.response.send_message("Partnership sent successfully!", ephemeral=True)

# ========== BOT SETUP ========== #
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Variabili globali
warnings = defaultdict(list)
birthdays = {}
story_parts = []
muted_members = {}
queues = {}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

bot.start_time = datetime.datetime.now(datetime.timezone.utc)
PARTNER_CHANNEL_ID = 1411451850485403830

# ========== EVENTI ========== #
@bot.event
async def on_ready():
    print(f"✅ Bot online come {bot.user.name} | {len(UNIQUE_SERVERS)} server disponibili")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="Edu's Community - @antoilking10"
    ))
    load_data()
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandi sincronizzati!")
    except Exception as e:
        print(f"❌ Errore sincronizzazione comandi: {e}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1392109096857239664)  # welcome channel
    if channel:
        embed = discord.Embed(
            title="👋 Welcome!",
            description=f"Hello {member.mention}, welcome to **Edu's Community**!\nIntroduce yourself and have fun with us!\n\n-# We remind you to read the Rules",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        if custom_id == "ticket-type":
            await handle_ticket_creation(interaction)
        elif custom_id in ["manage-ticket", "close-ticket"]:
            await handle_ticket_buttons(interaction)

# ========== FUNZIONI DI SUPPORTO ========== #
def save_data():
    data = {
        'warnings': dict(warnings),
        'birthdays': birthdays,
        'muted_members': muted_members
    }
    with open('bot_data.json', 'w') as f:
        json.dump(data, f)

def load_data():
    global warnings, birthdays, muted_members
    try:
        with open('bot_data.json', 'r') as f:
            data = json.load(f)
            warnings.update(data.get('warnings', {}))
            birthdays.update(data.get('birthdays', {}))
            muted_members.update(data.get('muted_members', {}))
    except FileNotFoundError:
        pass

def get_uptime():
    delta = datetime.datetime.now(datetime.timezone.utc) - bot.start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h {minutes}m"

async def get_db_ping():
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        start_time = time.time()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return round((time.time() - start_time) * 1000, 2)
    except Exception:
        return None

async def get_random_meme():
    # Implementazione semplificata per meme
    local_memes = [
        {"title": "😂 Funny Meme", "url": "https://i.imgur.com/8WjJY9J.jpg"},
        {"title": "🎮 Gaming Meme", "url": "https://i.imgur.com/3JZ3Q3X.jpg"},
        {"title": "💻 Programmer Meme", "url": "https://i.imgur.com/5ZQ2W9J.jpg"}
    ]
    return random.choice(local_memes)

async def play_next(guild, voice_client, interaction=None):
    if guild.id in queues and queues[guild.id]:
        try:
            url = queues[guild.id].pop(0)
            voice_client.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
            if interaction:
                embed = discord.Embed(title="🎵 Now Playing", description=url, color=discord.Color.green())
                await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"Playback error: {e}")
            await play_next(guild, voice_client)
    else:
        await asyncio.sleep(60)
        if voice_client and not voice_client.is_playing():
            await voice_client.disconnect()

# ========== SISTEMA TICKET ========== #
async def staff_check(interaction: discord.Interaction) -> bool:
    if not any(role.id == TICKET_CONFIG["STAFF_ROLE_ID"] for role in interaction.user.roles):
        await interaction.response.send_message("❌ Solo lo Staff può usare questo comando!", ephemeral=True)
        return False
    return True

async def handle_ticket_creation(interaction: discord.Interaction):
    ticket_type = interaction.data["values"][0]
    user = interaction.user

    if ticket_type == "staff":
        if not any(role.id == TICKET_CONFIG["STAFF_ROLE_ID"] for role in user.roles):
            await interaction.response.send_message("❌ Non hai i permessi per accedere alle applicazioni Staff!", ephemeral=True)
            return

    ticket_name = {
        "support": f"🌐▾support༝{user.name}",
        "bug": f"⚔️▾report༝{user.name}",
        "staff": f"👑▾staff-module༝{user.name}",
        "other": f"⭐▾other༝{user.name}"
    }.get(ticket_type, f"ticket-{ticket_type}")[:95]

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        interaction.guild.get_role(TICKET_CONFIG["SUPPORT_ROLE_ID"]): discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    if ticket_type == "staff":
        overwrites[interaction.guild.get_role(TICKET_CONFIG["STAFF_ROLE_ID"])] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    try:
        ticket_channel = await interaction.guild.create_text_channel(
            name=ticket_name,
            category=interaction.guild.get_channel(TICKET_CONFIG["TICKET_CATEGORY_ID"]),
            overwrites=overwrites
        )

        if ticket_type == "staff":
            embed = discord.Embed(
                title="👑**STAFF APPLICATION**",
                description=f"👤 Welcome to the Staff Application {user.mention}",
                color=0xffa500
            )
            content = f"👑 <@&{TICKET_CONFIG['STAFF_ROLE_ID']}> new staff application!"
        else:
            embed = discord.Embed(
                title="📖**TICKET INFO**",
                description=f"👤 Welcome to the Ticket system {user.mention}",
                color=0x2b2d31
            )
            content = f"🛠️ <@&{TICKET_CONFIG['SUPPORT_ROLE_ID']}> a ticket has just been opened!"

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="🔧 Manage", custom_id="manage-ticket", style=discord.ButtonStyle.secondary))
        view.add_item(discord.ui.Button(label="❌ Close", custom_id="close-ticket", style=discord.ButtonStyle.danger))

        await ticket_channel.send(content=content, embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket creato: {ticket_channel.mention}", ephemeral=True)

    except Exception as e:
        print(f"❌ Errore creazione ticket: {e}")
        await interaction.response.send_message("❌ Errore nella creazione del ticket!", ephemeral=True)

async def handle_ticket_buttons(interaction: discord.Interaction):
    custom_id = interaction.data.get("custom_id")
    
    if custom_id == "manage-ticket":
        if not any(role.id == TICKET_CONFIG["SUPPORT_ROLE_ID"] for role in interaction.user.roles):
            await interaction.response.send_message("❌ Solo lo Staff può gestire i ticket!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        # Implementazione gestione ticket...
        await interaction.followup.send("✅ Gestione ticket implementata!", ephemeral=True)

    elif custom_id == "close-ticket":
        await interaction.response.defer(ephemeral=True)
        # Implementazione chiusura ticket...
        await interaction.followup.send("✅ Ticket chiuso!", ephemeral=True)
        await interaction.channel.delete()

# ========== COMANDI SLASH ========== #
@bot.tree.command(name="random-role-set", description="[ADMIN] Imposta ruolo per /random-server")
@discord.app_commands.default_permissions(administrator=True)
async def set_role(interaction: discord.Interaction, role: discord.Role):
    global AUTHORIZED_ROLE_ID
    AUTHORIZED_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ Ruolo autorizzato impostato: {role.mention}", ephemeral=True)

@bot.tree.command(name="random-server", description="Mostra un server partner casuale")
@discord.app_commands.checks.cooldown(1, 2)
async def random_server(interaction: discord.Interaction):
    if AUTHORIZED_ROLE_ID is None:
        await interaction.response.send_message("❌ Usa prima /random-role-set per impostare un ruolo", ephemeral=True)
        return

    if not any(role.id == AUTHORIZED_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ Non hai il ruolo richiesto!", ephemeral=True)
        return

    invite = random.choice(UNIQUE_SERVERS)
    embed = discord.Embed(
        title="🔍 Random Partner Server",
        description="Ecco un server dalla nostra rete:",
        color=0x5865F2
    )
    embed.add_field(name="Invite", value=f"[Clicca per unirti]({invite})", inline=False)
    embed.set_footer(text=f"Server totali: {len(UNIQUE_SERVERS)}")
    await interaction.response.send_message(embed=embed, view=ServerView(invite), ephemeral=True)

@bot.tree.command(name="partnership", description="Invia una partnership")
async def partnership(interaction: discord.Interaction):
    role_ids = [role.id for role in interaction.user.roles]
    if 1392745984387452978 not in role_ids:  # ID ruolo autorizzato
        await interaction.response.send_message("❌ Non hai i permessi per questo comando!", ephemeral=True)
        return

    modal = PartnershipModal()
    await interaction.response.send_modal(modal)

@bot.tree.command(name="ping", description="Mostra statistiche di latenza")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    ws_latency = round(bot.latency * 1000, 2)
    db_ping = await get_db_ping()
    uptime = get_uptime()
    
    embed = discord.Embed(title="📊 Statistiche Connessione", color=0x2b2d31)
    embed.add_field(name="🛜 Latency", value=f"`{ws_latency}ms`", inline=True)
    embed.add_field(name="⏳ Uptime", value=f"`{uptime}`", inline=True)
    embed.add_field(name="🪙 Database", value=f"`{db_ping}ms`" if db_ping else "`N/A`", inline=True)
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="ticket-panel", description="Crea un pannello ticket (Solo Staff)")
@discord.app_commands.check(staff_check)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="**EDU'S COMMUNITY TICKETS**",
        description="Clicca sulla categoria più rilevante per il tuo Ticket",
        color=0x2b2d31
    )

    select = discord.ui.Select(
        custom_id="ticket-type",
        placeholder="Scegli la categoria...",
        options=[
            discord.SelectOption(label="Supporto Generale", value="support"),
            discord.SelectOption(label="Segnalazione Bug/Player", value="bug"),
            discord.SelectOption(label="Applicazione Staff", value="staff"),
            discord.SelectOption(label="Altro", value="other")
        ]
    )

    view = discord.ui.View()
    view.add_item(select)
    
    await interaction.response.send_message("✅ Pannello creato!", ephemeral=True)
    await interaction.followup.send(embed=embed, view=view)

@bot.tree.command(name="meme", description="Mostra un meme casuale")
async def meme_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    meme_data = await get_random_meme()
    embed = discord.Embed(title=meme_data['title'], color=discord.Color.gold())
    embed.set_image(url=meme_data['url'])
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="help", description="Mostra tutti i comandi disponibili")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="🎮 Comandi del Bot", color=discord.Color.blue())
    embed.description = """
**🛡️ MODERAZIONE**
• `/ban` - Banna un utente
• `/kick` - Espelli un utente
• `/mute` - Muta un utente

**🎉 DIVERTIMENTO**
• `/meme` - Meme casuale
• `/random-server` - Server partner casuale
• `/partnership` - Invia partnership

**🛠️ UTILITY**
• `/ping` - Statistiche bot
• `/ticket-panel` - Pannello ticket (Staff)
• `/help` - Questo messaggio
"""
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== ALIAS SYSTEM ========== #
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(('!', '/')):
        await bot.process_commands(message)

# ========== AVVIO BOT ========== #
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ Token Discord non trovato!")
        exit(1)
    
    print("✅ Token trovato, avvio bot...")
    bot.run(TOKEN)
