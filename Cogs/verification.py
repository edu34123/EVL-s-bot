async def send_english_rules_message(self):
    """Invia il regolamento INGLESE nel canale dedicato"""
    for guild in self.bot.guilds:
        channel = guild.get_channel(self.RULES_CHANNEL_ID)
        if channel:
            try:
                # Pulisci SOLO se è un canale diverso da quello italiano
                if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                    print(f"🔄 Pulizia canale regolamento inglese: #{channel.name}")
                    deleted_count = 0
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            try:
                                await message.delete()
                                deleted_count += 1
                                await asyncio.sleep(0.5)
                            except:
                                pass
                    
                    if deleted_count > 0:
                        print(f"🗑️ Eliminati {deleted_count} messaggi vecchi")
                
                await asyncio.sleep(2)
                
                # REGOLAMENTO INGLESE AGGIORNATO
                embed_eng = discord.Embed(
                    title="📜 SERVER RULES - ENGLISH 🇬🇧",
                    color=0x0099ff,
                    description="**Welcome to the server! Please read the rules carefully before participating.**"
                )
                
                # TESTO AGGIORNATO con le nuove regole
                rules_text = """
**1. RESPECT AND BEHAVIOR**
• Don't be toxic to other members!
• No insults, discrimination or hate speech
• Respect staff and their decisions

**2. PROHIBITED CONTENT**
• No NSFW allowed!
• No gore content!
• No slurs or offensive language!
• No spam or message flooding!

**3. PING AND MENTION RULES**
• Don't ping the admins!
• Only people with special roles can be pinged
• No ghost ping

**4. SAFETY AND PRIVACY**
• Don't share personal info!
• Only share personal information in ⁠👋・introductions channel
• No offensive profile pictures or names!
• No impersonation of other users!

**5. AGE AND LANGUAGE REQUIREMENTS**
• No users under 13 years allowed!
• Only English and Italian languages please!
• Respect Discord's Terms of Service!

**6. GENERAL RULES**
• Use appropriate channels for each content
• No off-topic in dedicated channels
• Follow staff instructions immediately

**⛔ SANCTIONS**
Failure to comply with these rules will result in:
• 🟡 **Warning** - First offense
• 🔴 **Temporary mute** - Repeated offenses
• 🔴 **Permanent ban** - Severe or repeated violations

By accepting these rules, you confirm you have read and accepted them.
"""
                
                embed_eng.add_field(
                    name="Complete Server Rules",
                    value=rules_text,
                    inline=False
                )
                
                # Aggiungi riferimento al canale italiano se esiste
                if self.RULES_CHANNEL_ID != self.ITALIAN_RULES_CHANNEL_ID:
                    italian_channel = guild.get_channel(self.ITALIAN_RULES_CHANNEL_ID)
                    if italian_channel:
                        embed_eng.add_field(
                            name="🇮🇹 Italian Rules",
                            value=f"For rules in Italian, visit {italian_channel.mention}",
                            inline=False
                        )
                
                embed_eng.set_footer(text="Server Rules - English Version • Last update")
                embed_eng.timestamp = discord.utils.utcnow()
                
                await channel.send(embed=embed_eng)
                print(f"✅ Regolamento INGLESE AGGIORNATO inviato in #{channel.name}")
                
            except Exception as e:
                print(f"❌ Errore invio regolamento inglese: {e}")
        else:
            print(f"❌ Canale regolamento inglese non trovato (ID: {self.RULES_CHANNEL_ID})")
