# Anonymous chatbot.

---
## Overview:
* Project is **completely asynchronous** thanks to [aiogram](https://github.com/aiogram/aiogram), [asyncpg](https://github.com/MagicStack/asyncpg) and [redis asyncio](https://github.com/redis/redis-py).
* It's easy to test and debug because 2 levels of logging are provided.
* The yookassa __test__ API is integrated.

---
## Setup:
1. Clone this repository:
```bash
git clone https://github.com/schr1k/AnonChat_2.0.git AnonChat
```
2. Create venv:
```bash
python -m venv venv
```
3. Activate venv:
* On Windows:
```bash
venv\Scripts\activate
```
* On Linux and macOS:
```bash
source venv/bin/activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Change credentials in config.py:
```python
TOKEN = 'token from BotFather'

# Postgres
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'postgres'
POSTGRES_DB = 'AnonChat'
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'

# Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1

# Yookassa
YOOKASSA_ACCOUNT_ID = 'yookassa shop id'
YOOKASSA_SECRET_KEY = 'yookassa api token'
RETURN_URL = 'link to your bot'
```

6. [Install Redis](https://redis.io/docs/getting-started/installation/).
7. [Install Postgres](https://www.postgresql.org/download/).
