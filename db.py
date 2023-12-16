import asyncpg

from config import *


class DB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB
        )

    # Init table creation ==============================================================================================
    async def create_tables(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR,
                    age VARCHAR,
                    sex VARCHAR,
                    tg VARCHAR,
                    connect_with VARCHAR,
                    last_connect VARCHAR,
                    chats INT DEFAULT 0,
                    messages INT DEFAULT 0,
                    likes INT DEFAULT 0,
                    dislikes INT DEFAULT 0,
                    refs INT DEFAULT 0,
                    points INT DEFAULT 0,
                    vip_ends VARCHAR(30),
                    notifications INT DEFAULT 1
                );''')

                await connection.execute('''
                CREATE TABLE IF NOT EXISTS queue (
                    tg VARCHAR,
                    sex VARCHAR,
                    op_sex VARCHAR
                );''')

                await connection.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    tg VARCHAR,
                    username VARCHAR,
                    message VARCHAR,
                    stamp VARCHAR
                );''')

    # SELECT ===========================================================================================================
    async def user_exists(self, tg: str) -> bool:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT tg FROM users WHERE tg = $1', tg
                )
                return False if result is None else True

    async def queue_exists(self, tg: str) -> bool:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT * FROM queue WHERE tg = $1', tg
                )
                return False if result is None else True

    async def count_users(self) -> str:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT COUNT(tg) FROM users'
                )
                return dict(result)['count']

    async def find_chat(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT tg FROM queue WHERE tg <> $1', tg
                )
                return dict(result)['tg'] if result is not None else None

    async def find_chat_vip(self, tg: str, sex: str, op_sex: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT tg FROM queue WHERE tg <> $1 AND (op_sex = $2 OR op_sex IS null) AND sex = $3', tg, sex, op_sex
                )
                return dict(result)['tg'] if result is not None else None

    async def select_name(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT name FROM users WHERE tg = $1', tg
                )
                return dict(result)['name']

    async def select_age(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT age FROM users WHERE tg = $1',
                    tg
                )
                return dict(result)['age']

    async def select_sex(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT sex FROM users WHERE tg = $1', tg
                )
                return dict(result)['sex']

    async def select_connect_with(self, tg: str) -> str:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT connect_with FROM users WHERE tg = $1', tg
                )
                return dict(result)['connect_with']

    async def select_connect_with_self(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT tg FROM users WHERE connect_with = $1', tg
                )
                return dict(result)['tg']

    async def select_last_connect(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT last_connect FROM users WHERE tg = $1', tg
                )
                return dict(result)['last_connect']

    async def select_chats(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT chats FROM users WHERE tg = $1', tg
                )
                return dict(result)['chats']

    async def select_messages(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT messages FROM users WHERE tg = $1', tg
                )
                return dict(result)['messages']

    async def select_likes(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT likes FROM users WHERE tg = $1', tg
                )
                return dict(result)['likes']

    async def select_dislikes(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT dislikes FROM users WHERE tg = $1', tg
                )
                return dict(result)['dislikes']

    async def select_vip_ends(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT vip_ends FROM users WHERE tg = $1', tg
                )
                return dict(result)['vip_ends']

    async def select_refs(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT refs FROM users WHERE tg = $1', tg
                )
                return dict(result)['refs']

    async def select_points(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT points FROM users WHERE tg = $1', tg
                )
                return dict(result)['points']

    async def select_notifications(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(
                    'SELECT notifications FROM users WHERE tg = $1', tg
                )
                return dict(result)['notifications']

    async def top_messages(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(
                    'SELECT name, messages FROM users ORDER BY messages DESC LIMIT 5'
                )
                top_dict = {}
                for number, value in enumerate(list(result)):
                    top_dict[number + 1] = {'name': dict(value)['name'], 'count': dict(value)['messages']}
                return top_dict

    async def top_refs(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(
                    'SELECT name, refs FROM users ORDER BY messages DESC LIMIT 5'
                )
                top_dict = {}
                for number, value in enumerate(list(result)):
                    top_dict[number + 1] = {'name': dict(value)['name'], 'count': dict(value)['refs']}
                return top_dict

    async def top_likes(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(
                    'SELECT name, likes FROM users ORDER BY messages DESC LIMIT 5'
                )
                top_dict = {}
                for number, value in enumerate(list(result)):
                    top_dict[number + 1] = {'name': dict(value)['name'], 'count': dict(value)['likes']}
                return top_dict

    async def count_users(self) -> int:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchval('SELECT COUNT(tg) FROM users')
                return result

    # UPDATE ===========================================================================================================
    async def update_name(self, tg: str, name: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET name = $1 WHERE tg = $2', name, tg
                )

    async def update_age(self, tg: str, age: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET age = $1 WHERE tg = $2', age, tg
                )

    async def update_sex(self, tg: str, sex: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET sex = $1 WHERE tg = $2', sex, tg
                )

    async def update_connect_with(self, tg: str, connect_with: str | None):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                if connect_with != tg:
                    await connection.execute(
                        'UPDATE users SET connect_with = $1 WHERE tg = $2', connect_with, tg
                    )

    async def update_last_connect(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET last_connect = connect_with WHERE tg = $1', tg
                )

    async def update_chats(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET chats = chats + 1 WHERE tg = $1', tg
                )

    async def update_messages(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET messages = messages + 1 WHERE tg = $1', tg
                )

    async def update_likes(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET likes = likes + 1 WHERE tg = $1', tg
                )

    async def update_dislikes(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET dislikes = dislikes + 1 WHERE tg = $1', tg
                )

    async def update_refs(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET refs = refs + 1 WHERE tg = $1', tg
                )

    async def update_points(self, tg: str, value: int):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET points = points + $1 WHERE tg = $2', value, tg
                )

    async def update_notifications(self, tg: str, value: int):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET notifications = $1 WHERE tg = $2', value, tg
                )

    async def update_vip_ends(self, tg: str, time: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'UPDATE users SET vip_ends = $1 WHERE tg = $2', time, tg
                )

    # INSERT ===========================================================================================================
    async def insert_in_users(self, tg: str, name: str, age: str, sex: str, vip_ends: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'INSERT INTO users (tg, name, age, sex, vip_ends) VALUES($1, $2, $3, $4, $5)', tg, name, age, sex, vip_ends
                )

    async def insert_in_queue(self, tg: str, sex: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'INSERT INTO queue (tg, sex, op_sex) VALUES($1, $2, $3)', tg, sex, None
                )

    async def insert_in_queue_vip(self, tg: str, sex: str, op_sex: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'INSERT INTO queue (tg, sex, op_sex) VALUES($1, $2, $3)', tg, sex, op_sex
                )

    async def insert_in_messages(self, tg: str, username: str, message: str, stamp: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'INSERT INTO messages (tg, username, message, stamp) VALUES ($1, $2, $3, $4)', tg, username, message, stamp
                )

    # DELETE ===========================================================================================================
    async def delete_from_queue(self, tg: str):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    'DELETE FROM queue WHERE tg = $1', tg
                )
