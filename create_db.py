import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


connection = psycopg2.connect(user='postgres', password='postgres', port='5432', database='AnonChat')
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = connection.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    state VARCHAR(20),
    name VARCHAR(20),
    age VARCHAR(3),
    sex VARCHAR(10),
    tg VARCHAR(20),
    connect_with VARCHAR(20),
    last_connect VARCHAR(20),
    chats INT DEFAULT 0,
    messages INT DEFAULT 0,
    likes INT DEFAULT 0,
    dislikes INT DEFAULT 0,
    vip_ends VARCHAR(30),
    refs INT DEFAULT 0,
    points INT DEFAULT 0,
    notifications INT DEFAULT 1,
    order_id INT DEFAULT 1
);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS queue (
    tg VARCHAR(15),
    sex VARCHAR(6),
    op_sex VARCHAR(6)
);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
    tg VARCHAR(15),
    message VARCHAR(15)
)''')
