import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command
from redis.asyncio import Redis

from config import *
import kb
from states import *
from db import DB
from payments import *

db = DB()

redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
)
storage = RedisStorage(redis)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

logging.basicConfig(filename="all.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s function: %(funcName)s line: %(lineno)d - %(message)s')
errors = logging.getLogger("errors")
errors.setLevel(logging.ERROR)
fh = logging.FileHandler("errors.log")
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s function: %(funcName)s line: %(lineno)d - %(message)s')
fh.setFormatter(formatter)
errors.addHandler(fh)


def top(word: str, top_dict: dict) -> str:
    st = ''
    for i, j in top_dict.items():
        st += f'{i}) {j["name"]} — <b>{j["count"]}</b> <i>{word}</i>.\n'
    return st


# Главная ==============================================================================================================
@dp.message(Command('start'))
async def start(message: Message, state: FSMContext):
    try:
        await state.clear()
        if not await db.user_exists(str(message.from_user.id)):
            sp = message.text.split()
            if len(sp) > 1:
                user_id = sp[1]
                await db.update_refs(str(user_id))
                await db.update_points(str(user_id), 1)
                if bool(await db.select_notifications(user_id)):
                    await bot.send_message(user_id, 'Кто-то присоединился к боту по вашей ссылке!')
                    if await db.select_refs(user_id) % 10 == 0:
                        await bot.send_message(user_id, 'Вы можете отключить уведомления о новых рефах в настройках.')
            await message.answer(f'Добро пожаловать в анонимный чат!\n'
                                 f'Перед тем как начать общение необходимо пройти регистрацию.\n'
                                 f'После регистрации вы получите <b>вип на неделю бесплатно!</b>\n'
                                 f'Продолжая пользование ботом вы соглашаетесь с правилами.\n',
                                 reply_markup=kb.lobby_kb, parse_mode='HTML')
        else:
            await message.answer(f'Привет, {await db.select_name(str(message.from_user.id))}.', reply_markup=kb.main_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'to_main')
async def call_start(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Привет, {await db.select_name(str(call.from_user.id))}.',
                                    reply_markup=kb.main_kb)
    except Exception as e:
        errors.error(e)


# Лобби ================================================================================================================
@dp.callback_query(F.data == 'lobby')
async def lobby(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Добро пожаловать в анонимный чат!\n'
                                         f'Перед тем как начать общение необходимо пройти регистрацию.\n'
                                         f'После регистрации вы получите <b>вип на неделю бесплатно!</b>\n'
                                         f'Продолжая пользование ботом вы соглашаетесь с правилами.\n',
                                    reply_markup=kb.lobby_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


@dp.message(Command('help'))
async def help(message: Message):
    try:
        await message.answer(f'/start - В начало')
    except Exception as e:
        errors.error(e)


@dp.message(Command('bug'))
async def bug(message: Message, state: FSMContext):
    try:
        await message.answer('Опишите ошибку с которой вы столкнулись.')
        await state.set_state(Bug.bug)
    except Exception as e:
        errors.error(e)


@dp.message(Bug.bug)
async def set_bug(message: Message, state: FSMContext):
    try:
        sender = message.from_user.id if message.from_user.username is None else f'@{message.from_user.username}'
        await bot.send_message(BUGS_GROUP_ID, f'Отправитель: {sender}.\n'
                                              f'Сообщение: {message.text}.')
        await message.answer('Разработчик оповещен о проблеме и скоро ее исправит.\n'
                             'Спасибо за помощь!')
        await state.clear()
    except Exception as e:
        errors.error(e)


@dp.message(Command('idea'))
async def idea(message: Message, state: FSMContext):
    try:
        await message.answer('Что вы хотите предложить?')
        await state.set_state(Idea.idea)
    except Exception as e:
        errors.error(e)


@dp.message(Idea.idea)
async def set_idea(message: Message, state: FSMContext):
    try:
        sender = message.from_user.id if message.from_user.username is None else f'@{message.from_user.username}'
        await bot.send_message(IDEAS_GROUP_ID, f'Отправитель: {sender}.\n'
                                               f'Сообщение: {message.text}.')
        await message.answer('Идея передана разработчику.\n'
                             'Спасибо за помощь!')
        await state.clear()
    except Exception as e:
        errors.error(e)


# Правила ==============================================================================================================
@dp.callback_query(F.data == 'rules')
async def rules(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<b>В чате запрещены:</b>\n'
                                         f'1) Любые упоминания психоактивных веществ (наркотиков).\n'
                                         f'2) Обмен, распространение любых 18+ материалов.\n'
                                         f'3) Любая реклама, спам, продажа чего либо.\n'
                                         f'4) Оскорбительное поведение.\n'
                                         f'5) Любые действия, нарушающие правила Telegram.\n',
                                    reply_markup=kb.to_lobby_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Регистрация ==========================================================================================================
@dp.callback_query(F.data == 'registrate')
async def registrate(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Введите ваше имя.')
        await state.set_state(RegState.name)
    except Exception as e:
        errors.error(e)


@dp.message(RegState.name)
async def reg_name(message: Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.answer('Введите ваш возраст.')
        await state.set_state(RegState.age)
    except Exception as e:
        errors.error(e)


@dp.message(RegState.age)
async def reg_age(message: Message, state: FSMContext):
    try:
        await state.update_data(age=message.text)
        await message.answer('Выберите ваш пол.', reply_markup=kb.sex_kb)
        await state.set_state(RegState.sex)
    except Exception as e:
        errors.error(e)


@dp.callback_query(RegState.sex, F.data.endswith('male'))
async def reg_sex(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await state.update_data(sex=call.data)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Регистрация завершена.\nВам выдан вип на 7 дней.', reply_markup=kb.main_kb)
        data = await state.get_data()
        await db.insert_in_users(str(call.from_user.id), data['name'], data['age'], data['sex'],
                                 (datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y %H:%M'))
        await state.clear()
    except Exception as e:
        errors.error(e)


# Профиль ==============================================================================================================
@dp.callback_query(F.data == 'profile')
async def profile(call: CallbackQuery):
    try:
        await call.answer()
        sex = 'Неизвестно'
        if await db.select_sex(str(call.from_user.id)) == 'male':
            sex = 'Мужской'
        elif await db.select_sex(str(call.from_user.id)) == 'female':
            sex = 'Женский'
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'🅰️ <b>Имя:</b> <i>{await db.select_name(str(call.from_user.id))}</i>\n'
                                         f'🔞 <b>Возраст:</b> <i>{await db.select_age(str(call.from_user.id))}</i>\n'
                                         f'👫 <b>Пол:</b> <i>{sex}</i>',
                                    reply_markup=kb.profile_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Настройки ============================================================================================================
@dp.callback_query(F.data == 'settings')
async def settings(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Что вы хотите изменить?', reply_markup=kb.settings_kb)
    except Exception as e:
        errors.error(e)


# Имя ==================================================================================================================
@dp.callback_query(F.data == 'name')
async def edit_name(call: CallbackQuery, state: FSMContext):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Введите свое имя.')
        await state.set_state(NameState.name)
    except Exception as e:
        errors.error(e)


@dp.message(NameState.name)
async def set_name(message: Message, state: FSMContext):
    try:
        await db.update_name(str(message.from_user.id), message.text)
        await message.answer(text='Имя сохранено.', reply_markup=kb.to_settings_kb)
        await state.clear()
    except Exception as e:
        errors.error(e)


# Возраст ==============================================================================================================
@dp.callback_query(F.data == 'age')
async def edit_age(call: CallbackQuery, state: FSMContext):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Введите свой возраст.')
        await state.set_state(AgeState.age)
    except Exception as e:
        errors.error(e)


@dp.message(AgeState.age)
async def set_age(message: Message, state: FSMContext):
    try:
        await db.update_age(str(message.from_user.id), message.text)
        await message.answer('Возраст сохранен.', reply_markup=kb.to_settings_kb)
        await state.clear()
    except Exception as e:
        errors.error(e)


# Пол ==================================================================================================================
@dp.callback_query(F.data == 'sex')
async def edit_sex(call: CallbackQuery, state: FSMContext):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Выберите свой пол.', reply_markup=kb.sex_kb)
        await state.set_state(SexState.sex)
    except Exception as e:
        errors.error(e)


@dp.callback_query(SexState.sex, F.data.endswith('male'))
async def set_sex(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await db.update_sex(str(call.from_user.id), call.data)
        await bot.send_message(call.from_user.id, 'Пол сохранен.', reply_markup=kb.to_settings_kb)
        await state.clear()
    except Exception as e:
        errors.error(e)


# Статистика ===========================================================================================================
@dp.callback_query(F.data == 'stats')
async def stats(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'💬 Чатов: {await db.select_chats(str(call.from_user.id))}\n'
                                         f'⌨️ Сообщений: {await db.select_messages(str(call.from_user.id))}\n'
                                         f'👍 Лайков: {await db.select_likes(str(call.from_user.id))}\n'
                                         f'👎 Дизлайков: {await db.select_dislikes(str(call.from_user.id))}\n'
                                         f'👨‍💻 Пользователей приглашено: {await db.select_refs(str(call.from_user.id))}',
                                    reply_markup=kb.statistic_kb)
    except Exception as e:
        errors.error(e)


# Рефералка ============================================================================================================
@dp.callback_query(F.data == 'ref')
async def ref(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Распространяйте свою реферальную ссылку, чтобы получать 💎.\n'
                                         f'1 переход по ссылке = 1 💎.\n'
                                         f'5 💎 = 1 день VIP-статуса 👑.\n'
                                         f'У вас {await db.select_points(str(call.from_user.id))} 💎.\n\n'
                                         f'🆔 Ваша реферальная ссылка:\n'
                                         f'{f"{RETURN_URL}?start=" + str(str(call.from_user.id))}.',
                                    disable_web_page_preview=True,
                                    reply_markup=kb.ref_kb(await db.select_notifications(str(call.from_user.id))))
    except Exception as e:
        errors.error(e)


# Обмен 💎 =============================================================================================================
@dp.callback_query(F.data == 'trade')
async def trade(call: CallbackQuery):
    try:
        if await db.select_points(str(call.from_user.id)) >= 5:
            await db.update_points(str(call.from_user.id), -5)
            if await db.select_vip_ends(str(call.from_user.id)) is None:
                await db.update_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
                                         str(call.from_user.id))
                await call.answer('Успешно!')
            else:
                await db.update_vip_ends(
                    (datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') +
                     timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), str(call.from_user.id))
            await call.answer('Успешно!')
        else:
            await call.answer('У вас недостаточно баллов.')
    except Exception as e:
        errors.error(e)


# Уведомления ==========================================================================================================
@dp.callback_query(F.data == 'on')
async def notifications_on(call: CallbackQuery):
    try:
        await call.answer()
        await db.update_notifications(str(call.from_user.id), 1)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Уведомления включены.', reply_markup=kb.to_ref_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'off')
async def notifications_off(call: CallbackQuery):
    try:
        await call.answer()
        await db.update_notifications(str(call.from_user.id), 0)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Уведомления выключены.', reply_markup=kb.to_ref_kb)
    except Exception as e:
        errors.error(e)


# Топы =================================================================================================================
@dp.callback_query(F.data == 'tops')
async def tops(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Ниже представлены рейтинги по разным критериям.', reply_markup=kb.top_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'top_messages')
async def top_messages(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('сообщений', await db.top_messages()), reply_markup=kb.to_tops_kb,
                                    parse_mode='HTML')
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'top_likes')
async def top_likes(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('лайков', await db.top_likes()), reply_markup=kb.to_tops_kb,
                                    parse_mode='HTML')
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'top_refs')
async def top_refs(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('рефов', await db.top_refs()), reply_markup=kb.to_tops_kb,
                                    parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Вип ==================================================================================================================
@dp.callback_query(F.data == 'vip')
async def vip(call: CallbackQuery):
    try:
        await call.answer()
        if await db.select_vip_ends(str(call.from_user.id)) is not None:
            if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
                delta = datetime.strptime(await db.select_vip_ends(str(call.from_user.id)),
                                          '%d.%m.%Y %H:%M') - datetime.now()
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=f'Осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds // 60 % 60} минут Випа.',
                                            reply_markup=kb.vip_kb)
            else:
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=f'Вип дает:\n'
                                                 f'1) Поиск по полу.\n'
                                                 f'2) Подробная информацию о собеседнике: отзывы, имя, пол, возраст.\n'
                                                 f'<b>Сейчас подключены ТЕСТОВЫЕ платежи, то есть деньги НЕ будут списаны, но вип вы получите.</b>',
                                            reply_markup=kb.vip_kb, parse_mode='HTML')
        else:
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=f'Вип дает:\n'
                                             f'1) Поиск по полу.\n'
                                             f'2) Подробная информацию о собеседнике: отзывы, имя, пол, возраст.\n'
                                             f'<b>Сейчас подключены ТЕСТОВЫЕ платежи, то есть деньги НЕ будут списаны, но вип вы получите.</b>',
                                        reply_markup=kb.vip_kb, parse_mode='HTML')
    except Exception as e:
        errors.error(e)


# Купить вип ===========================================================================================================
@dp.callback_query(F.data == 'buy_vip')
async def buy_vip(call: CallbackQuery):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Выберите длительность:', reply_markup=kb.buy_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'vip_day')
async def buy_day(call: CallbackQuery):
    try:
        await call.answer()
        url, payment_id = create_payment(20, 'Вип на 1 день')
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<a href="{url}">Оплатить 20 рублей</a>', parse_mode='HTML',
                                    reply_markup=kb.to_buy_kb)
        c = 0
        paid = False
        while True:
            if get_payment_status(payment_id) == 'waiting_for_capture':
                paid = True
                break
            elif c == 600:
                await bot.send_message(call.from_user.id, 'Платеж отменен.\n'
                                                          'Причина: прошло 10 минут с момента создания платежа.',
                                       reply_markup=kb.to_main_kb)
                break
            else:
                await asyncio.sleep(1)
                c += 1
        if paid:
            response = json.loads(confirm_payment(payment_id))
            if response['status'] == 'succeeded':
                await db.update_vip_ends(str(call.from_user.id), (
                    datetime.strptime(str(await db.select_vip_ends(str(call.from_user.id))),
                                      '%d.%m.%Y %H:%M') + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'))
                await bot.send_message(call.from_user.id, 'Вы успешно приобрели вип на 1 день.\n'
                                                          'Приятного пользования!', reply_markup=kb.to_main_kb)
            else:
                await bot.send_message(call.from_user.id, 'Произошла ошибка.\n'
                                                          'Деньги будут возвращены вам в течение 24 часов.',
                                       reply_markup=kb.to_main_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'vip_week')
async def buy_week(call: CallbackQuery):
    try:
        await call.answer()
        url, payment_id = create_payment(100, 'Вип на 1 неделю')
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<a href="{url}">Оплатить 100 рублей</a>', parse_mode='HTML',
                                    reply_markup=kb.to_buy_kb)
        c = 0
        paid = False
        while True:
            if get_payment_status(payment_id) == 'waiting_for_capture':
                paid = True
                break
            elif c == 600:
                await bot.send_message(call.from_user.id, 'Платеж отменен.\n'
                                                          'Причина: прошло 10 минут с момента создания платежа.',
                                       reply_markup=kb.to_main_kb)
                break
            else:
                await asyncio.sleep(1)
                c += 1
        if paid:
            response = json.loads(confirm_payment(payment_id))
            if response['status'] == 'succeeded':
                await db.update_vip_ends(str(call.from_user.id),
                                         (datetime.strptime(str(await db.select_vip_ends(str(call.from_user.id))),
                                                            '%d.%m.%Y %H:%M') + timedelta(days=7)).strftime(
                                             '%d.%m.%Y %H:%M'))
                await bot.send_message(call.from_user.id, 'Вы успешно приобрели вип на 1 неделю.\n'
                                                          'Приятного пользования!', reply_markup=kb.to_main_kb)
            else:
                await bot.send_message(call.from_user.id, 'Произошла ошибка.\n'
                                                          'Деньги будут возвращены вам в течение 24 часов.',
                                       reply_markup=kb.to_main_kb)
    except Exception as e:
        errors.error(e)


@dp.callback_query(F.data == 'vip_month')
async def buy_month(call: CallbackQuery):
    try:
        await call.answer()
        url, payment_id = create_payment(300, 'Вип на 1 месяц')
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<a href="{url}">Оплатить 300 рублей</a>', parse_mode='HTML',
                                    reply_markup=kb.to_buy_kb)
        c = 0
        paid = False
        while True:
            if get_payment_status(payment_id) == 'waiting_for_capture':
                paid = True
                break
            elif c == 600:
                await bot.send_message(call.from_user.id, 'Платеж отменен.\n'
                                                          'Причина: прошло 10 минут с момента создания платежа.',
                                       reply_markup=kb.to_main_kb)
                break
            else:
                await asyncio.sleep(1)
                c += 1
        if paid:
            response = json.loads(confirm_payment(payment_id))
            if response['status'] == 'succeeded':
                await db.update_vip_ends(str(call.from_user.id), (
                    datetime.strptime(str(await db.select_vip_ends(str(call.from_user.id))),
                                      '%d.%m.%Y %H:%M') + timedelta(days=30)).strftime('%d.%m.%Y %H:%M'))
                await bot.send_message(call.from_user.id, 'Вы успешно приобрели вип на 1 месяц.\n'
                                                          'Приятного пользования!', reply_markup=kb.to_main_kb)
            else:
                await bot.send_message(call.from_user.id, 'Произошла ошибка.\n'
                                                          'Деньги будут возвращены вам в течение 24 часов.',
                                       reply_markup=kb.to_main_kb)
    except Exception as e:
        errors.error(e)


# Поиск ================================================================================================================
@dp.callback_query(F.data == 'search')
async def search(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await db.insert_in_queue(str(call.from_user.id), await db.select_sex(str(call.from_user.id)))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Ищем собеседника... 🔍', reply_markup=kb.cancel_search_kb)
        while True:
            await asyncio.sleep(0.5)
            if await db.find_chat(str(call.from_user.id)) is not None:
                await db.update_connect_with(str(call.from_user.id), await db.find_chat(str(call.from_user.id)))
                break
        while True:
            await asyncio.sleep(0.5)
            if await db.select_connect_with(str(call.from_user.id)) is not None:
                await db.delete_from_queue(str(call.from_user.id))
                break
        await bot.send_message(call.from_user.id, 'Нашли для тебя собеседника 🥳\n'
                                                  '/stop - остановить диалог')
        if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
            sex = 'Неизвестно'
            user_id = str(await db.select_connect_with(str(call.from_user.id)))
            if await db.select_sex(user_id) == 'male':
                sex = 'Мужской'
            elif await db.select_sex(user_id) == 'female':
                sex = 'Женский'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Имя: {await db.select_name(user_id)}\n'
                                   f'🔞 Возраст: {await db.select_age(user_id)}\n'
                                   f'👫 Пол: {sex}\n'
                                   f'👍: {await db.select_likes(user_id)} 👎: {await db.select_dislikes(user_id)}\n', )
        await state.set_state(Chatting.msg)
    except Exception as e:
        errors.error(e)


# Поиск ♂️ =============================================================================================================
@dp.callback_query(F.data == 'search_man')
async def search_man(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
            await db.insert_in_queue_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)), 'male')
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Ищем собеседника... 🔍', reply_markup=kb.cancel_search_kb)
            while True:
                await asyncio.sleep(0.5)
                if await db.find_chat_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)),
                                          'male') is not None:
                    await db.update_connect_with(
                        str(call.from_user.id), await db.find_chat_vip(str(call.from_user.id),
                                                                       await db.select_sex(str(call.from_user.id)),
                                                                       'male'))
                    break
            while True:
                await asyncio.sleep(0.5)
                if await db.select_connect_with(str(call.from_user.id)) is not None:
                    await db.delete_from_queue(str(call.from_user.id))
                    break
            await bot.send_message(call.from_user.id, 'Нашли для тебя собеседника 🥳\n'
                                                      '/stop - остановить диалог')
            sex = 'Неизвестно'
            user_id = str(await db.select_connect_with(str(call.from_user.id)))
            if await db.select_sex(user_id) == 'male':
                sex = 'Мужской'
            elif await db.select_sex(user_id) == 'female':
                sex = 'Женский'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Имя: {await db.select_name(user_id)}\n'
                                   f'🔞 Возраст: {await db.select_age(user_id)}\n'
                                   f'👫 Пол: {sex}\n'
                                   f'👍: {await db.select_likes(user_id)} 👎: {await db.select_dislikes(user_id)}\n')
            await state.set_state(Chatting.msg)
        else:
            await call.answer()
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Поиск по полу доступен только для вип-пользователей',
                                        reply_markup=kb.sex_search_no_vip_kb)
    except Exception as e:
        errors.error(e)


# Поиск ♀️ =============================================================================================================
@dp.callback_query(F.data == 'search_woman')
async def search_woman(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        if datetime.strptime(await db.select_vip_ends(str(call.from_user.id)), '%d.%m.%Y %H:%M') > datetime.now():
            await db.insert_in_queue_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)), 'female')
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Ищем собеседника... 🔍', reply_markup=kb.cancel_search_kb)
            while True:
                await asyncio.sleep(0.5)
                if await db.find_chat_vip(str(call.from_user.id), await db.select_sex(str(call.from_user.id)),
                                          'female') is not None:
                    await db.update_connect_with(
                        str(call.from_user.id), await db.find_chat_vip(str(call.from_user.id),
                                                                       await db.select_sex(str(call.from_user.id)),
                                                                       'female'))
                    break
            while True:
                await asyncio.sleep(0.5)
                if await db.select_connect_with(str(call.from_user.id)) is not None:
                    await db.delete_from_queue(str(call.from_user.id))
                    break
            await bot.send_message(call.from_user.id, 'Нашли для тебя собеседника 🥳\n'
                                                      '/stop - остановить диалог')
            sex = 'Неизвестно'
            user_id = str(await db.select_connect_with(str(call.from_user.id)))
            if await db.select_sex(user_id) == 'male':
                sex = 'Мужской'
            elif await db.select_sex(user_id) == 'female':
                sex = 'Женский'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Имя: {await db.select_name(user_id)}\n'
                                   f'🔞 Возраст: {await db.select_age(user_id)}\n'
                                   f'👫 Пол: {sex}\n'
                                   f'👍: {await db.select_likes(user_id)} 👎: {await db.select_dislikes(user_id)}\n')
            await state.set_state(Chatting.msg)
        else:
            await call.answer()
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Поиск по полу доступен только для вип-пользователей',
                                        reply_markup=kb.sex_search_no_vip_kb)
    except Exception as e:
        errors.error(e)


# Отменить поиск =======================================================================================================
@dp.callback_query(F.data == 'cancel_search')
async def cancel_search(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Поиск отменен 😥.',
                                    reply_markup=kb.main_kb)
        await db.delete_from_queue(str(call.from_user.id))
    except Exception as e:
        errors.error(e)


# Лайк =================================================================================================================
@dp.callback_query(F.data == 'like')
async def like(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Спасибо за отзыв!', reply_markup=kb.review_kb)
        await db.update_likes(await db.select_last_connect(str(call.from_user.id)))
    except Exception as e:
        errors.error(e)


# Дизлайк ==============================================================================================================
@dp.callback_query(F.data == 'dislike')
async def dislike(call: CallbackQuery):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Спасибо за отзыв!', reply_markup=kb.review_kb)
        await db.update_dislikes(await db.select_last_connect(str(call.from_user.id)))
    except Exception as e:
        errors.error(e)


# Ссылка ===============================================================================================================
@dp.message(Chatting.msg, Command('link'))
async def link(message: Message):
    try:
        if message.from_user.username is None:
            await message.answer('Введите юзернейм в настройках телеграма!')
        else:
            await bot.send_message(await db.select_connect_with(str(message.from_user.id)),
                                   f'Собеседник отправил свой юзернейм: @{message.from_user.username}.')
            await message.answer('Юзернейм отправлен!')
    except Exception as e:
        errors.error(e)


# Остановить диалог ====================================================================================================
@dp.message(Chatting.msg, Command('stop'))
async def stop(message: Message, state: FSMContext):
    try:
        op_state = FSMContext(
            storage=storage,
            key=StorageKey(
                chat_id=int(await db.select_connect_with(str(message.from_user.id))),
                user_id=int(await db.select_connect_with(str(message.from_user.id))),
                bot_id=bot.id)
        )
        await bot.send_message(message.from_user.id,
                               'Диалог остановлен 😞\nВы можете оценить собеседника ниже.',
                               reply_markup=kb.search_kb)
        await bot.send_message(await db.select_connect_with(str(message.from_user.id)),
                               'Диалог остановлен 😞\nВы можете оценить собеседника ниже.',
                               reply_markup=kb.search_kb)
        await db.update_chats(await db.select_connect_with(str(message.from_user.id)))
        await db.update_chats(str(message.from_user.id))
        await db.update_last_connect(await db.select_connect_with(str(message.from_user.id)))
        await db.update_last_connect(str(message.from_user.id))
        await db.update_connect_with(await db.select_connect_with(str(message.from_user.id)), None)
        await db.update_connect_with(str(message.from_user.id), None)
        await state.clear()
        await op_state.clear()
    except Exception as e:
        errors.error(e)


# Общение ==============================================================================================================
@dp.message(Chatting.msg, F.text)
async def chatting_text(message: Message):
    try:
        await bot.send_message(await db.select_connect_with(str(message.from_user.id)), message.text)
        await db.insert_in_messages(str(message.from_user.id), message.from_user.username, message.text,
                                    datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        await db.update_messages(str(message.from_user.id))
    except Exception as e:
        errors.error(e)


# Фото =================================================================================================================
@dp.message(Chatting.msg, F.photo)
async def chatting_photo(message: Message):
    try:
        await bot.send_photo(await db.select_connect_with(str(message.from_user.id)), message.photo[-1].file_id)
    except Exception as e:
        errors.error(e)


# Видео ================================================================================================================
@dp.message(Chatting.msg, F.video)
async def chatting_video(message: Message):
    try:
        await bot.send_video(await db.select_connect_with(str(message.from_user.id)), message.video.file_id)
    except Exception as e:
        errors.error(e)


# Гиф ==================================================================================================================
@dp.message(Chatting.msg, F.animation)
async def chatting_animation(message: Message):
    try:
        await bot.send_animation(await db.select_connect_with(str(message.from_user.id)), message.animation.file_id)
    except Exception as e:
        errors.error(e)


# Стикер ===============================================================================================================
@dp.message(Chatting.msg, F.sticker)
async def chatting_sticker(message: Message):
    try:
        await bot.send_sticker(await db.select_connect_with(str(message.from_user.id)), message.sticker.file_id)
    except Exception as e:
        errors.error(e)


# Документ =============================================================================================================
@dp.message(Chatting.msg, F.document)
async def chatting_document(message: Message):
    try:
        await bot.send_document(await db.select_connect_with(str(message.from_user.id)), message.document.file_id)
    except Exception as e:
        errors.error(e)


# Аудио ================================================================================================================
@dp.message(Chatting.msg, F.audio)
async def chatting_audio(message: Message):
    try:
        await bot.send_audio(await db.select_connect_with(str(message.from_user.id)), message.audio.file_id)
    except Exception as e:
        errors.error(e)


# Гс ===================================================================================================================
@dp.message(Chatting.msg, F.voice)
async def chatting_voice(message: Message):
    try:
        await bot.send_voice(await db.select_connect_with(str(message.from_user.id)), message.voice.file_id)
    except Exception as e:
        errors.error(e)


# Кружок ===============================================================================================================
@dp.message(Chatting.msg, F.video_note)
async def chatting_video_note(message: Message):
    try:
        await bot.send_video_note(await db.select_connect_with(str(message.from_user.id)), message.video_note.file_id)
    except Exception as e:
        errors.error(e)


# Остальное ===============================================================================================================
@dp.message(Chatting.msg, F.unknown)
async def chatting_unknown(message):
    try:
        await message.answer('Этот тип контента пока не поддерживается 😢.')
    except Exception as e:
        errors.error(e)


# id ===================================================================================================================
@dp.message(Command('id'))
async def ids(message: Message):
    try:
        await message.answer(str(message.from_user.id))
    except Exception as e:
        errors.error(e)


# group id =============================================================================================================
@dp.message(Command('gid'))
async def gids(message: Message):
    try:
        await message.answer(str(message.chat.id))
    except Exception as e:
        errors.error(e)


# all ==================================================================================================================
@dp.message()
async def all(message: Message):
    try:
        if str(message.chat.id) not in [BUGS_GROUP_ID, IDEAS_GROUP_ID]:
            await message.answer('Команда не распознана. Отправьте /start для выхода в главное меню.')
    except Exception as e:
        errors.error(e)


async def main():
    await db.connect()
    await db.create_tables()
    await dp.start_polling(bot)


if __name__ == '__main__':
    print(f'Бот запущен ({datetime.now().strftime("%H:%M:%S %d.%m.%Y")}).')
    asyncio.run(main())
