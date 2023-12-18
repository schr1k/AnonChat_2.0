> Readme на русском доступно [здесь](./README_ru.md).

## Overview:
* Project is **completely asynchronous** thanks to [aiogram](https://github.com/aiogram/aiogram), [asyncpg](https://github.com/MagicStack/asyncpg) and [redis asyncio](https://github.com/redis/redis-py).
* It's easy to test and debug because 2 levels of logging are provided.
* The [yookassa](https://yookassa.ru/developers?lang=en) **test** API is integrated.

### Setup:
1. Telegram:
   * Create new bot via [BotFather](https://t.me/BotFather).
   * Create groups (not channels) for bug reports and ideas, add your bot to them and give him admin rights (to get group id forward a message from it to this [bot](https://t.me/getmyid_bot)).

2. Create yookassa [test shop](https://yookassa.ru/my/boarding?shopMenuAction=createShop).

3. Create .env file with following structure ([dotenv guide](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1)):

```dotenv
# Telegram
TOKEN='token from BotFather'
BUGS_GROUP_ID='group id' # starts with "-"
IDEAS_GROUP_ID='group id' # starts with "-"
RETURN_URL='link to your bot' # needed for yookassa

# Postgres
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='postgres'
POSTGRES_DB='AnonChat'
POSTGRES_HOST='localhost' # change it to container name if you use docker
POSTGRES_PORT='5432'

# Redis
REDIS_DB='1'
REDIS_HOST='localhost' # change it to container name if you use docker
REDIS_PORT='6379'

# Yookassa
YOOKASSA_ACCOUNT_ID='yookassa shop id' # note that this value should be int
YOOKASSA_SECRET_KEY='yookassa api token'
```

### Running:
The easiest way is to run project via [docker](https://docs.docker.com/).
1. Make sure you have installed [docker](https://docs.docker.com/get-docker/).

2. Build the project (it may take some time):
```bash
docker compose build
```

3. Run the project:
```bash
docker compose up
```

That's all! [Docker compose file](./docker-compose.yaml) will install and configure everything.

---
Alternatively you can run it manually:
1. Create venv:
```bash
python -m venv venv
```

2. Activate venv:

* On Windows:
```bash
venv\Scripts\activate
```
* On Linux and macOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install [Redis](https://redis.io/docs/getting-started/installation/).

5. Install [Postgres](https://www.postgresql.org/download/) (if you changed user or password during installation make sure to also change it in [.env file](./.env)).

6. Run the project:
```bash
python main.py
```

---
Feel free to [ask questions](https://github.com/schr1k/AnonChat_2.0/discussions/categories/q-a) and [share your ideas](https://github.com/schr1k/AnonChat_2.0/discussions/categories/ideas).

Plans on the project are [here](https://github.com/users/schr1k/projects/3).