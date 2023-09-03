import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import exceptions, executor
from aiopayok import Payok

import config
import kb
from states import RegState, AgeState, NameState, SexState, Chatting
from db import DB

db = DB()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(filename="all_log.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)
fh = logging.FileHandler("warning_log.log")
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(funcName)s: %(message)s (%(lineno)d)')
fh.setFormatter(formatter)
warning_log.addHandler(fh)

pay = Payok(api_id=config.API_ID, api_key=config.API_KEY, secret_key=config.SECRET_KEY, shop=config.SHOP_ID)


def top(word: str, list_top: list) -> str:
    st = ''
    for i in range(len(list_top)):
        st += f'{i + 1}) {list_top[i][0]} — <b>{list_top[i][1]}</b> <i>{word}</i>\n'
    return st


# Главная ==============================================================================================================
@dp.message_handler(commands=['start'])
async def start(message):
    try:
        if not db.user_exists(message.from_user.id):
            sp = message.text.split()
            if len(sp) > 1:
                user_id = sp[1]
                db.update_refs(1, user_id)
                db.update_points(1, user_id)
                if bool(db.select_notifications(user_id)):
                    await bot.send_message(user_id, 'Кто-то присоединился к боту по вашей ссылке!')
                    if db.select_refs(user_id) % 10 == 0:
                        await bot.send_message(user_id, 'Вы можете отключить уведомления о новых рефах в настройках.')
            await message.answer(f'Добро пожаловать в анонимный чат!\n'
                                 f'Перед тем как начать общение необходимо пройти регистрацию.\n'
                                 f'После регистрации вы получите <b>вип на неделю бесплатно!</b>\n'
                                 f'Продолжая пользование ботом вы соглашаетесь с правилами.\n',
                                 reply_markup=kb.lobby_kb, parse_mode='HTML')
        else:
            await message.answer(f'Привет, {db.select_name(message.from_user.id)}', reply_markup=kb.main_kb)
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'to_main', state='*')
async def call_start(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Привет, {db.select_name(call.from_user.id)}', reply_markup=kb.main_kb)
    except Exception as e:
        warning_log.warning(e)


# Лобби ================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'lobby')
async def lobby(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Добро пожаловать в анонимный чат!\n'
                                         f'Перед тем как начать общение необходимо пройти регистрацию.\n'
                                         f'После регистрации вы получите <b>вип на неделю бесплатно!</b>\n'
                                         f'Продолжая пользование ботом вы соглашаетесь с правилами.\n',
                                    reply_markup=kb.lobby_kb, parse_mode='HTML')
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(commands=['help'])
async def help(message):
    try:
        await message.answer(f'/start - В начало')
    except Exception as e:
        warning_log.warning(e)


# Правила ==============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'rules')
async def rules(call):
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
        warning_log.warning(e)


# Регистрация ==========================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'registrate')
async def registrate(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Введите ваше имя.')
        await RegState.name.set()
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(state=RegState.name)
async def reg_name(message, state):
    try:
        await state.update_data(name=message.text)
        await message.answer('Введите ваш возраст.')
        await RegState.age.set()
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(state=RegState.age)
async def reg_age(message, state):
    try:
        await state.update_data(age=message.text)
        await message.answer('Выберите ваш пол.', reply_markup=kb.sex_kb)
        await RegState.sex.set()
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data.endswith('male'), state=RegState.sex)
async def reg_sex(call, state):
    try:
        await call.answer()
        await state.update_data(sex=call.data)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Регистрация завершена.\nВам выдан вип на 7 дней.', reply_markup=kb.main_kb)
        data = await state.get_data()
        db.insert_in_users(data['name'], data['age'], data['sex'], call.from_user.id,
                           (datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y %H:%M'))
        await state.finish()
    except Exception as e:
        warning_log.warning(e)


# Профиль ==============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'profile')
async def profile(call):
    try:
        await call.answer()
        sex = 'Неизвестно'
        if db.select_sex(call.from_user.id) == 'male':
            sex = 'Мужской'
        elif db.select_sex(call.from_user.id) == 'female':
            sex = 'Женский'
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'🅰️ <b>Имя:</b> <i>{db.select_name(call.from_user.id)}</i>\n'
                                         f'🔞 <b>Возраст:</b> <i>{db.select_age(call.from_user.id)}</i>\n'
                                         f'👫 <b>Пол:</b> <i>{sex}</i>',
                                    reply_markup=kb.profile_kb, parse_mode='HTML')
    except Exception as e:
        warning_log.warning(e)


# Настройки ============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'settings')
async def settings(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Что вы хотите изменить?', reply_markup=kb.settings_kb)
    except Exception as e:
        warning_log.warning(e)


# Имя ==================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'name')
async def edit_name(call):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Введите свое имя.')
        await NameState.name.set()
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(state=NameState.name)
async def set_name(message, state):
    try:
        await state.update_data(name=message.text)
        data = await state.get_data()
        db.update_name(data['name'], message.from_user.id)
        await message.answer('Имя сохранено.', reply_markup=kb.to_main_kb)
        await state.finish()
    except Exception as e:
        warning_log.warning(e)


# Возраст ==============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'age')
async def edit_age(call):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Введите свой возраст.')
        await AgeState.age.set()
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(state=AgeState.age)
async def set_age(message, state):
    try:
        await state.update_data(age=message.text)
        data = await state.get_data()
        db.update_age(data['age'], message.from_user.id)
        await message.answer('Возраст сохранен.', reply_markup=kb.to_main_kb)
        await state.finish()
    except Exception as e:
        warning_log.warning(e)


# Пол ==================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'sex')
async def edit_sex(call):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Выберите свой пол.', reply_markup=kb.sex_kb)
        await SexState.sex.set()
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data.endswith('male'), state=SexState.sex)
async def set_sex(call, state):
    try:
        await call.answer()
        await state.update_data(sex=call.data)
        data = await state.get_data()
        db.update_sex(data['sex'], call.from_user.id)
        await bot.send_message(call.from_user.id, 'Пол сохранен.', reply_markup=kb.to_main_kb)
        await state.finish()
    except Exception as e:
        warning_log.warning(e)


# Статистика ===========================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'stats')
async def stats(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'💬 Чатов: {db.select_chats(call.from_user.id)}\n'
                                         f'⌨️ Сообщений: {db.select_messages(call.from_user.id)}\n'
                                         f'👍 Лайков: {db.select_likes(call.from_user.id)}\n'
                                         f'👎 Дизлайков: {db.select_dislikes(call.from_user.id)}\n'
                                         f'👨‍💻 Пользователей приглашено: {db.select_refs(call.from_user.id)}',
                                    reply_markup=kb.statistic_kb)

    except Exception as e:
        warning_log.warning(e)


# Рефералка ============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'ref')
async def ref(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'Распространяйте свою реферальную ссылку, чтобы получать 💎.\n'
                                         f'1 переход по ссылке = 1 💎.\n'
                                         f'5 💎 = 1 день VIP-статуса 👑.\n'
                                         f'У вас {db.select_points(call.from_user.id)} 💎.\n\n'
                                         f'🆔 Ваша реферальная ссылка:\n'
                                         f'{f"{config.RETURN_URL}?start=" + str(call.from_user.id)}.',
                                    disable_web_page_preview=True,
                                    reply_markup=kb.ref_kb(db.select_notifications(call.from_user.id)))
    except Exception as e:
        warning_log.warning(e)


# Обмен 💎 =============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'trade')
async def trade(call):
    try:
        if db.select_points(call.from_user.id) >= 5:
            db.update_points(-5, call.from_user.id)
            if db.select_vip_ends(call.from_user.id) is None:
                db.update_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
                                   call.from_user.id)
                await call.answer('Успешно!')
            else:
                db.update_vip_ends((datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') +
                                    timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), call.from_user.id)
            await call.answer('Успешно!')
        else:
            await call.answer('У вас недостаточно баллов.')
    except Exception as e:
        warning_log.warning(e)


# Уведомления ==========================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'on')
async def notifications_on(call):
    try:
        await call.answer()
        db.update_notifications(1, call.from_user.id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Уведомления включены.', reply_markup=kb.to_ref_kb)
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'off')
async def notifications_off(call):
    try:
        await call.answer()
        db.update_notifications(0, call.from_user.id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Уведомления выключены.', reply_markup=kb.to_ref_kb)
    except Exception as e:
        warning_log.warning(e)


# Топы =================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'tops')
async def tops(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Ниже представлены рейтинги по разным критериям.', reply_markup=kb.top_kb)
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'top_messages')
async def top_messages(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('сообщений', db.top_messages()), reply_markup=kb.to_tops_kb, parse_mode='HTML')
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'top_likes')
async def top_likes(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('лайков', db.top_likes()), reply_markup=kb.to_tops_kb, parse_mode='HTML')
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'top_refs')
async def top_refs(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=top('рефов', db.top_refs()), reply_markup=kb.to_tops_kb, parse_mode='HTML')
    except Exception as e:
        warning_log.warning(e)


# Вип ==================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'vip')
async def vip(call):
    try:
        await call.answer()
        if db.select_vip_ends(call.from_user.id) is not None:
            if datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') > datetime.now():
                delta = datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') - datetime.now()
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=f'Осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds // 60 % 60} минут Випа.',
                                            reply_markup=kb.vip_kb)
            else:
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=f'Вип дает:\n'
                                                 f'1) Поиск по полу.\n'
                                                 f'2) Подробная информацию о собеседнике: отзывы, имя, пол, возраст, страна...\n'
                                                 f'3) <b>Первое место в очереди.</b>\n'
                                                 f'<i>Это далеко не все, функции будут постоянно добавляться</i>.',
                                            reply_markup=kb.vip_kb, parse_mode='HTML')
        else:
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=f'Вип дает:\n'
                                             f'1) Поиск по полу.\n'
                                             f'2) Подробная информацию о собеседнике: отзывы, имя, возраст, пол, страна, город\n'
                                             f'3) <b>Первое место в очереди.</b>\n'
                                             f'<i>Это далеко не все, функции будут постоянно добавляться</i>.',
                                        reply_markup=kb.vip_kb, parse_mode='HTML')
    except Exception as e:
        warning_log.warning(e)


# Купить вип ===========================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'buy_vip')
async def buy_vip(call):
    try:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Выберите длительность:', reply_markup=kb.buy_kb)
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'vip_day')
async def buy_day(call):
    try:
        await call.answer()
        c = 0
        db.update_order_id(call.from_user.id)
        payment_id = f'{call.from_user.id}-{int(db.select_order_id(call.from_user.id)) + 1}'
        payments = await pay.create_pay(amount=20, currency='RUB', success_url=config.RETURN_URL, desc=payment_id,
                                        payment=payment_id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<a href="{payments}">Оплатить 20 рублей</a>', parse_mode='HTML')
        flag1 = False
        while not flag1:
            for i in [dict(i) for i in list(await pay.get_transactions())]:
                if i['payment_id'] == payment_id:
                    if c >= 3600:
                        flag1 = True
                        break
                    if i['transaction_status'] == 1:
                        await call.answer('Успешно')
                        if db.select_vip_ends(call.from_user.id) is None:
                            db.update_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
                                               call.from_user.id)
                        else:
                            db.update_vip_ends(
                                (datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') +
                                 timedelta(days=1)).strftime('%d.%m.%Y %H:%M'), call.from_user.id)
                        flag1 = True
                        break
                    else:
                        await asyncio.sleep(3)
                        c += 3
                else:
                    await asyncio.sleep(3)
                    c += 3
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'vip_week')
async def buy_week(call):
    try:
        await call.answer()
        c = 0
        db.update_order_id(call.from_user.id)
        payment_id = f'{call.from_user.id}-{int(db.select_order_id(call.from_user.id)) + 1}'
        payments = await pay.create_pay(amount=100, currency='RUB', success_url=config.RETURN_URL, desc=payment_id,
                                        payment=payment_id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<a href="{payments}">Оплатить 100 рублей</a>', parse_mode='HTML')
        flag1 = False
        while not flag1:
            for i in [dict(i) for i in list(await pay.get_transactions())]:
                if i['payment_id'] == payment_id:
                    if c >= 3600:
                        flag1 = True
                        break
                    if i['transaction_status'] == 1:
                        await call.answer('Успешно')
                        if db.select_vip_ends(call.from_user.id) is None:
                            db.update_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
                                               call.from_user.id)
                        else:
                            db.update_vip_ends(
                                (datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') +
                                 timedelta(days=7)).strftime('%d.%m.%Y %H:%M'), call.from_user.id)
                        flag1 = True
                        break
                    else:
                        await asyncio.sleep(3)
                        c += 3
                else:
                    await asyncio.sleep(3)
                    c += 3
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(lambda call: call.data == 'vip_month')
async def buy_month(call):
    try:
        await call.answer()
        c = 0
        db.update_order_id(call.from_user.id)
        payment_id = f'{call.from_user.id}-{int(db.select_order_id(call.from_user.id)) + 1}'
        payments = await pay.create_pay(amount=300, currency='RUB', success_url=config.RETURN_URL, desc=payment_id,
                                        payment=payment_id)
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=f'<a href="{payments}">Оплатить 300 рублей</a>', parse_mode='HTML')
        flag1 = False
        while not flag1:
            for i in [dict(i) for i in list(await pay.get_transactions())]:
                if i['payment_id'] == payment_id:
                    if c >= 3600:
                        flag1 = True
                        break
                    if i['transaction_status'] == 1:
                        await call.answer('Успешно')
                        if db.select_vip_ends(call.from_user.id) is None:
                            db.update_vip_ends((datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M'),
                                               call.from_user.id)
                        else:
                            db.update_vip_ends(
                                (datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') +
                                 timedelta(days=31)).strftime('%d.%m.%Y %H:%M'), call.from_user.id)
                        flag1 = True
                        break
                    else:
                        await asyncio.sleep(3)
                        c += 3
                else:
                    await asyncio.sleep(3)
                    c += 3
    except Exception as e:
        warning_log.warning(e)


# Поиск ================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'search', state='*')
async def search(call):
    try:
        await call.answer()
        db.insert_in_queue(call.from_user.id, db.select_sex(call.from_user.id))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Ищем собеседника... 🔍', reply_markup=kb.cancel_search_kb)
        while True:
            await asyncio.sleep(1)
            if db.find_chat(call.from_user.id) is not None:
                db.update_connect_with(db.find_chat(call.from_user.id)[0], call.from_user.id)
                db.update_connect_with(call.from_user.id, db.find_chat(call.from_user.id)[0])
                break
        while True:
            await asyncio.sleep(1)
            if db.select_connect_with(call.from_user.id) is not None:
                db.delete_from_queue(call.from_user.id)
                db.delete_from_queue(db.select_connect_with(call.from_user.id))
                break
        await bot.send_message(call.from_user.id, 'Нашли для тебя собеседника 🥳\n'
                                                  '/stop - остановить диалог')
        if datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') > datetime.now():
            sex = 'Неизвестно'
            user_id = db.select_connect_with(call.from_user.id)
            if db.select_sex(user_id) == 'male':
                sex = 'Мужской'
            elif db.select_sex(user_id) == 'female':
                sex = 'Женский'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Имя: {db.select_name(user_id)}\n'
                                   f'🔞 Возраст: {db.select_age(user_id)}\n'
                                   f'👫 Пол: {sex}\n'
                                   f'👍: {db.select_likes(user_id)} 👎: {db.select_dislikes(user_id)}\n', )
        await Chatting.msg.set()
    except Exception as e:
        warning_log.warning(e)


# Отменить поиск =======================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'cancel_search')
async def cancel_search(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Поиск отменен 😥.',
                                    reply_markup=kb.main_kb)
        db.delete_from_queue(call.from_user.id)
    except Exception as e:
        warning_log.warning(e)


# Лайк =================================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'like', state='*')
async def like(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Спасибо за отзыв!', reply_markup=kb.review_kb)
        db.update_likes(1, db.select_last_connect(call.from_user.id))
    except Exception as e:
        warning_log.warning(e)


# Дизлайк ==============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'dislike', state='*')
async def dislike(call):
    try:
        await call.answer()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text='Спасибо за отзыв!', reply_markup=kb.review_kb)
        db.update_dislikes(1, db.select_last_connect(call.from_user.id))
    except Exception as e:
        warning_log.warning(e)


# Поиск ♂️ =============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'search_man')
async def search_man(call):
    try:
        await call.answer()
        if datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') > datetime.now():
            db.insert_in_queue_vip(call.from_user.id, db.select_sex(call.from_user.id), 'male')
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Ищем собеседника... 🔍', reply_markup=kb.cancel_search_kb)
            while True:
                await asyncio.sleep(0.5)
                if db.find_chat_vip(call.from_user.id, db.select_sex(call.from_user.id), 'male') is not None:
                    db.update_connect_with(
                        db.find_chat_vip(call.from_user.id, db.select_sex(call.from_user.id), 'male'),
                        call.from_user.id)
                    db.update_connect_with(
                        call.from_user.id, db.find_chat_vip(call.from_user.id,
                                                            db.select_sex(call.from_user.id), 'male'))
                    break
            while True:
                await asyncio.sleep(0.5)
                if db.select_connect_with(call.from_user.id) is not None:
                    db.delete_from_queue(call.from_user.id)
                    db.delete_from_queue(db.select_connect_with(call.from_user.id))
                    break
            await bot.send_message(call.from_user.id, 'Нашли для тебя собеседника 🥳\n'
                                                      '/stop - остановить диалог')
            await bot.send_message(db.select_connect_with(call.from_user.id), 'Нашли для тебя собеседника 🥳\n'
                                                                              '/stop - остановить диалог')
            sex = 'Неизвестно'
            user_id = db.select_connect_with(call.from_user.id)
            if db.select_sex(user_id) == 'male':
                sex = 'Мужской'
            elif db.select_sex(user_id) == 'female':
                sex = 'Женский'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Имя: {db.select_name(user_id)}\n'
                                   f'🔞 Возраст: {db.select_age(user_id)}\n'
                                   f'👫 Пол: {sex}\n'
                                   f'👍: {db.select_likes(user_id)} 👎: {db.select_dislikes(user_id)}\n')
            if datetime.strptime(db.select_vip_ends(db.select_connect_with(call.from_user.id)),
                                 '%d.%m.%Y %H:%M') > datetime.now():
                sex = 'Неизвестно'
                user_id = call.from_user.id
                if db.select_sex(user_id) == 'male':
                    sex = 'Мужской'
                elif db.select_sex(user_id) == 'female':
                    sex = 'Женский'
                await bot.send_message(db.select_connect_with(call.from_user.id),
                                       f'🅰️ Имя: {db.select_name(user_id)}\n'
                                       f'🔞 Возраст: {db.select_age(user_id)}\n'
                                       f'👫 Пол: {sex}\n'
                                       f'👍: {db.select_likes(user_id)} 👎: {db.select_dislikes(user_id)}\n')
        else:
            await call.answer('Поиск по полу доступен только для вип-пользователей')
    except Exception as e:
        warning_log.warning(e)


# Поиск ♀️ =============================================================================================================
@dp.callback_query_handler(lambda call: call.data == 'search_woman')
async def search_woman(call):
    try:
        await call.answer()
        if datetime.strptime(db.select_vip_ends(call.from_user.id), '%d.%m.%Y %H:%M') > datetime.now():
            db.insert_in_queue_vip(call.from_user.id, db.select_sex(call.from_user.id), 'female')
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text='Ищем собеседника... 🔍', reply_markup=kb.cancel_search_kb)
            while True:
                await asyncio.sleep(0.5)
                if db.find_chat_vip(call.from_user.id, db.select_sex(call.from_user.id), 'female') is not None:
                    db.update_connect_with(
                        db.find_chat_vip(call.from_user.id, db.select_sex(call.from_user.id), 'female'),
                        call.from_user.id)
                    db.update_connect_with(
                        call.from_user.id, db.find_chat_vip(call.from_user.id,
                                                            db.select_sex(call.from_user.id), 'female'))
                    break
            while True:
                await asyncio.sleep(0.5)
                if db.select_connect_with(call.from_user.id) is not None:
                    db.delete_from_queue(call.from_user.id)
                    db.delete_from_queue(db.select_connect_with(call.from_user.id))
                    break
            await bot.send_message(call.from_user.id, 'Нашли для тебя собеседника 🥳\n'
                                                      '/stop - остановить диалог')
            await bot.send_message(db.select_connect_with(call.from_user.id), 'Нашли для тебя собеседника 🥳\n'
                                                                              '/stop - остановить диалог')
            sex = 'Неизвестно'
            user_id = db.select_connect_with(call.from_user.id)
            if db.select_sex(user_id) == 'male':
                sex = 'Мужской'
            elif db.select_sex(user_id) == 'female':
                sex = 'Женский'
            await bot.send_message(call.from_user.id,
                                   f'🅰️ Имя: {db.select_name(user_id)}\n'
                                   f'🔞 Возраст: {db.select_age(user_id)}\n'
                                   f'👫 Пол: {sex}\n'
                                   f'👍: {db.select_likes(user_id)} 👎: {db.select_dislikes(user_id)}\n')
            if datetime.strptime(db.select_vip_ends(db.select_connect_with(call.from_user.id)),
                                 '%d.%m.%Y %H:%M') > datetime.now():
                sex = 'Неизвестно'
                user_id = call.from_user.id
                if db.select_sex(user_id) == 'male':
                    sex = 'Мужской'
                elif db.select_sex(user_id) == 'female':
                    sex = 'Женский'
                await bot.send_message(db.select_connect_with(call.from_user.id),
                                       f'🅰️ Имя: {db.select_name(user_id)}\n'
                                       f'🔞 Возраст: {db.select_age(user_id)}\n'
                                       f'👫 Пол: {sex}\n'
                                       f'👍: {db.select_likes(user_id)} 👎: {db.select_dislikes(user_id)}\n')
        else:
            await call.answer('Поиск по полу доступен только для вип-пользователей')
    except Exception as e:
        warning_log.warning(e)


# Ссылка ===============================================================================================================
@dp.message_handler(commands=['link'], state=Chatting.msg)
async def link(message):
    try:
        if message.from_user.username is None:
            await message.answer('Введите юзернейм в настройках телеграма!')
        else:
            await bot.send_message(db.select_connect_with(message.from_user.id),
                                   f'Собеседник отправил свой юзернейм: @{message.from_user.username}.')
            await message.answer('Юзернейм отправлен!')
    except Exception as e:
        warning_log.warning(e)


# Остановить диалог ====================================================================================================
@dp.message_handler(commands=['stop'], state=Chatting.msg)
async def stop(message, state):
    try:
        await bot.send_message(message.from_user.id,
                               'Диалог остановлен 😞\nВы можете оценить собеседника ниже.',
                               reply_markup=kb.search_kb)
        await bot.send_message(db.select_connect_with(message.from_user.id),
                               'Диалог остановлен 😞\nВы можете оценить собеседника ниже.',
                               reply_markup=kb.search_kb)
        db.update_chats(1, db.select_connect_with(message.from_user.id))
        db.update_chats(1, message.from_user.id)
        db.update_last_connect(db.select_connect_with(message.from_user.id))
        db.update_last_connect(message.from_user.id)
        db.update_connect_with(None, db.select_connect_with(message.from_user.id))
        db.update_connect_with(None, message.from_user.id)
        await state.finish()
        op_state = dp.current_state(chat=db.select_connect_with(message.from_user.id), user=db.select_connect_with(message.from_user.id))
        await op_state.finish()
    except Exception as e:
        warning_log.warning(e)


# Общение ==============================================================================================================
@dp.message_handler(content_types=['text'], state=Chatting.msg)
async def chatting_text(message, state: FSMContext):
    try:
        await state.update_data(msg=message.text)
        user_data = await state.get_data()
        await bot.send_message(db.select_connect_with(message.from_user.id), user_data['msg'])
        db.insert_in_messages(message.from_user.id, user_data['msg'])
        db.update_messages(1, message.from_user.id)
    except exceptions.BotBlocked:
        await message.answer('Пользователь заблокировал бота!')
    except Exception as e:
        warning_log.warning(e)


# Фото =================================================================================================================
@dp.message_handler(content_types=['photo'], state=Chatting.msg)
async def chatting_photo(message, state: FSMContext):
    try:
        await state.update_data(photo=message.photo[-1].file_id)
        user_data = await state.get_data()
        await bot.send_photo(db.select_connect_with(message.from_user.id), user_data['photo'])
    except Exception as e:
        warning_log.warning(e)


# Видео ================================================================================================================
@dp.message_handler(content_types=['video'], state=Chatting.msg)
async def chatting_video(message, state: FSMContext):
    try:
        await state.update_data(video=message.video.file_id)
        user_data = await state.get_data()
        await bot.send_video(db.select_connect_with(message.from_user.id), user_data['video'])
    except Exception as e:
        warning_log.warning(e)


# Гиф ==================================================================================================================
@dp.message_handler(content_types=['animation'], state=Chatting.msg)
async def chatting_animation(message, state: FSMContext):
    try:
        await state.update_data(animation=message.animation.file_id)
        user_data = await state.get_data()
        await bot.send_animation(db.select_connect_with(message.from_user.id), user_data['animation'])
    except Exception as e:
        warning_log.warning(e)


# Стикер ===============================================================================================================
@dp.message_handler(content_types=['sticker'], state=Chatting.msg)
async def chatting_sticker(message, state: FSMContext):
    try:
        await state.update_data(sticker=message.sticker.file_id)
        user_data = await state.get_data()
        await bot.send_sticker(db.select_connect_with(message.from_user.id), user_data['sticker'])
    except Exception as e:
        warning_log.warning(e)


# Документ =============================================================================================================
@dp.message_handler(content_types=['document'], state=Chatting.msg)
async def chatting_document(message, state: FSMContext):
    try:
        await state.update_data(document=message.document.file_id)
        user_data = await state.get_data()
        await bot.send_document(db.select_connect_with(message.from_user.id), user_data['document'])
    except Exception as e:
        warning_log.warning(e)


# Аудио ================================================================================================================
@dp.message_handler(content_types=['audio'], state=Chatting.msg)
async def chatting_audio(message, state: FSMContext):
    try:
        await state.update_data(audio=message.audio.file_id)
        user_data = await state.get_data()
        await bot.send_audio(db.select_connect_with(message.from_user.id), user_data['audio'])
    except Exception as e:
        warning_log.warning(e)


# Гс ===================================================================================================================
@dp.message_handler(content_types=['voice'], state=Chatting.msg)
async def chatting_voice(message, state: FSMContext):
    try:
        await state.update_data(voice=message.voice.file_id)
        user_data = await state.get_data()
        await bot.send_voice(db.select_connect_with(message.from_user.id), user_data['voice'])
    except Exception as e:
        warning_log.warning(e)


# Кружок ===============================================================================================================
@dp.message_handler(content_types=['video_note'], state=Chatting.msg)
async def chatting_video_note(message, state: FSMContext):
    try:
        await state.update_data(video_note=message.video_note.file_id)
        user_data = await state.get_data()
        await bot.send_video_note(db.select_connect_with(message.from_user.id), user_data['video_note'])
    except Exception as e:
        warning_log.warning(e)


# Остальное ===============================================================================================================
@dp.message_handler(content_types=['unknown'], state=Chatting.msg)
async def chatting_unknown(message):
    try:
        await message.answer('Этот тип контента пока не поддерживается 😢.')
    except Exception as e:
        warning_log.warning(e)


if __name__ == '__main__':
    print('Работаем👌')
    executor.start_polling(dp, skip_updates=False)
