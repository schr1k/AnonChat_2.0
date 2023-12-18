> Readme on english is available [here](./README.md).

## Обзор:
* Проект **полностью асинхронен** благодаря [aiogram](https://github.com/aiogram/aiogram), [asyncpg](https://github.com/MagicStack/asyncpg) и [redis asyncio](https://github.com/redis/redis-py).
* Предусмотренно 2 уровня логирования.
* Подключен **тестовый** магазин [yookassa](https://yookassa.ru/developers?lang=en).

### Установка:
1. Telegram:
    * Создайте бота через [BotFather](https://t.me/BotFather).
    * Создайте группы (не каналы) для отслеживания багов и идей, добавьте в них вашего бота и сделайте бота админом этих групп (чтобы получить id канала, перешлите любое сообщение оттуда этому [боту](https://t.me/getmyid_bot)).

2. Создайте [тестовый магазин](https://yookassa.ru/my/boarding?shopMenuAction=createShop) юкасса.

3. Создайте .env файл с такой структурой ([гайд по dotenv](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1)):

```dotenv
# Telegram
TOKEN='token from BotFather'
BUGS_GROUP_ID='group id' # начинается на "-"
IDEAS_GROUP_ID='group id' # начинается на  "-"
RETURN_URL='link to your bot' # нужно для юкассы

# Postgres
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='postgres'
POSTGRES_DB='AnonChat'
POSTGRES_HOST='localhost' # измените на название контейнера если вы используете докер
POSTGRES_PORT='5432'

# Redis
REDIS_DB='1'
REDIS_HOST='localhost' # измените на название контейнера если вы используете докер
REDIS_PORT='6379'

# Yookassa
YOOKASSA_ACCOUNT_ID='yookassa shop id' # это значение должно быть числом
YOOKASSA_SECRET_KEY='yookassa api token'
```

### Запуск:
Самый простой способ - запустить проект с помощью [docker](https://docs.docker.com/).
1. Убедитесь, что у вас установлен [docker](https://docs.docker.com/get-docker/).

2. Скомпилируйте проект (это займет некоторое время):
```bash
docker compose build
```

3. Запустите проект:
```bash
docker compose up
```

На этом все! [Docker compose файл](./docker-compose.yaml) установит и настроит все необходимое.

---
Также вы можете запустить проект вручную:
1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:

* Windows:
```bash
venv\Scripts\activate
```
* Linux и macOS:
```bash
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Установите [Redis](https://redis.io/docs/getting-started/installation/).

5. Установите [Postgres](https://www.postgresql.org/download/) (если вы меняли имя пользователя или пароль при установке измените их в [.env файле](./.env)).

6. Запустите проект:
```bash
python main.py
```

---
Вы можете [задать вопрос](https://github.com/schr1k/AnonChat_2.0/discussions/categories/q-a) или [поделиться идеей](https://github.com/schr1k/AnonChat_2.0/discussions/categories/ideas) о проекте.

Планы по проекту находятся [здесь](https://github.com/users/schr1k/projects/3).