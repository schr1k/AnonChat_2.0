import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DB:
    def __init__(self):
        self.connection = psycopg2.connect(user='postgres', password='postgres', port='5432', database='AnonChat')
        self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.connection.cursor()

# SELECT ===============================================================================================================
    
    def user_exists(self, tg):
        self.cursor.execute(
                'SELECT tg FROM users WHERE tg = %s',
                (str(tg),)
            )
        return False if self.cursor.fetchone() is None else True
    
    def queue_exists(self, tg):
        self.cursor.execute(
                'SELECT * FROM queue WHERE tg = %s',
                (str(tg),)
            )
        return False if self.cursor.fetchone() is None else True

    def count_users(self):
        self.cursor.execute(
                'SELECT COUNT(tg) FROM users'
            )
        return self.cursor.fetchone()[0]
    
    def find_chat(self, tg):
        self.cursor.execute(
                'SELECT tg FROM queue WHERE tg <> %s',
                (str(tg),)
            )
        return self.cursor.fetchone()

    def find_chat_vip(self, tg, sex, op_sex):
        self.cursor.execute(
                'SELECT tg FROM queue WHERE tg <> %s AND op_sex = %s AND sex = %s',
                (str(tg), sex, op_sex)
            )
        return self.cursor.fetchone()[0]

    # Инфа =============================================

    def select_state(self, tg):
        self.cursor.execute(
                'SELECT state FROM users WHERE tg = %s', 
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_name(self, tg):
        self.cursor.execute(
                'SELECT name FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_age(self, tg):
        self.cursor.execute(
                'SELECT age FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_sex(self, tg):
        self.cursor.execute(
                'SELECT sex FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_connect_with(self, tg):
        self.cursor.execute(
                'SELECT connect_with FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_connect_with_self(self, tg):
        self.cursor.execute(
                'SELECT tg FROM users WHERE connect_with = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_last_connect(self, tg):
        self.cursor.execute(
                'SELECT last_connect FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_chats(self, tg):
        self.cursor.execute(
                'SELECT chats FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_messages(self, tg):
        self.cursor.execute(
                'SELECT messages FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_likes(self, tg):
        self.cursor.execute(
                'SELECT likes FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_dislikes(self, tg):
        self.cursor.execute(
                'SELECT dislikes FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_vip_ends(self, tg):
        self.cursor.execute(
                'SELECT vip_ends FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_refs(self, tg):
        self.cursor.execute(
                'SELECT refs FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_points(self, tg):
        self.cursor.execute(
                'SELECT points FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_notifications(self, tg):
        self.cursor.execute(
                'SELECT notifications FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    def select_order_id(self, tg):
        self.cursor.execute(
                'SELECT order_id FROM users WHERE tg = %s',
                (str(tg),)
            )
        return self.cursor.fetchone()[0]

    # Топы =====================================================================
    def top_messages(self):
        self.cursor.execute(
                'SELECT name, messages FROM users ORDER BY messages DESC LIMIT 5'
            )
        return self.cursor.fetchall()

    def top_refs(self):
        self.cursor.execute(
                'SELECT name, refs FROM users ORDER BY refs DESC LIMIT 5'
            )
        return self.cursor.fetchall()

    def top_likes(self):
        self.cursor.execute(
                'SELECT name, likes FROM users ORDER BY likes DESC LIMIT 5'
            )
        return self.cursor.fetchall()

# UPDATE ===============================================================================================================

    def update_state(self, state, tg):
        self.cursor.execute(
                'UPDATE users SET state = %s WHERE tg = %s',
                (state, str(tg))
            )

    def update_name(self, name, tg):
        self.cursor.execute(
                'UPDATE users SET name = %s WHERE tg = %s',
                (name, str(tg))
            )

    def update_age(self, age, tg):
        self.cursor.execute(
                'UPDATE users SET age = %s WHERE tg = %s',
                (age, str(tg))
            )

    def update_sex(self, sex, tg):
        self.cursor.execute(
                'UPDATE users SET sex = %s WHERE tg = %s',
                (sex, str(tg))
            )

    def update_connect_with(self, connect_with, tg):
        if connect_with != tg:
            self.cursor.execute(
                    'UPDATE users SET connect_with = %s WHERE tg = %s',
                    (str(connect_with), str(tg))
                )

    def update_last_connect(self, tg):
        self.cursor.execute(
                'UPDATE users SET last_connect = connect_with WHERE tg = %s',
                (str(tg),)
            )

    def update_chats(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET chats = chats + %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_messages(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET messages = messages + %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_likes(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET likes = likes + %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_dislikes(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET dislikes = dislikes + %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_vip_ends(self, time, tg):
        self.cursor.execute(
                'UPDATE users SET vip_ends = %s WHERE tg = %s',
                (time, str(tg))
            )

    def update_refs(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET refs = refs + %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_points(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET points = points + %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_notifications(self, value, tg):
        self.cursor.execute(
                'UPDATE users SET notifications = %s WHERE tg = %s',
                (value, str(tg))
            )

    def update_order_id(self, tg):
        self.cursor.execute(
                'UPDATE users SET order_id = order_id + 1 WHERE tg = %s',
                (str(tg),)
            )

# INSERT ===============================================================================================================

    def insert_in_users(self, name, age, sex, tg, vip_ends):
        self.cursor.execute(
                'INSERT INTO users (name, age, sex, tg, vip_ends)'
                'VALUES(%s, %s, %s, %s, %s)',
                (name, age, sex, str(tg), vip_ends)
            )

    def insert_in_queue(self, tg, sex):
        self.cursor.execute(
                'INSERT INTO queue (tg, sex, op_sex) '
                'VALUES(%s, %s, %s)',
                (str(tg), sex, None)
            )

    def insert_in_queue_vip(self, tg, sex, op_sex):
        self.cursor.execute(
                'INSERT INTO queue (tg, sex, op_sex) '
                'VALUES(%s, %s, %s)',
                (str(tg), sex, op_sex)
            )

    def insert_in_messages(self, tg, message):
        self.cursor.execute(
                'INSERT INTO messages (tg, message)'
                'VALUES (%s, %s)',
                (str(tg), message)
            )

# DELETE ===============================================================================================================

    def delete_from_queue(self, tg):
        self.cursor.execute(
                'DELETE FROM queue WHERE tg = %s',
                (str(tg),)
            )


# db = DB()
# print(db.update_connect_with('123', '886971306'))
# print(db.user_exists('123'))
