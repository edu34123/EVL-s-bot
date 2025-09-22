import aiosqlite # type: ignore

class Database:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
    
    async def get_user_level(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT level, xp FROM levels WHERE user_id = ? AND guild_id = ?',
                (user_id, guild_id)
            )
            return await cursor.fetchone()
    
    async def get_leaderboard(self, guild_id, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT user_id, level, xp FROM levels WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT ?',
                (guild_id, limit)
            )
            return await cursor.fetchall()