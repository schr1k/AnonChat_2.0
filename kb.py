from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
                          InlineKeyboardMarkup, InlineKeyboardButton

# Назад ================================================================================================================
to_main = InlineKeyboardButton('🔙 На главную', callback_data='to_main')
to_ref = InlineKeyboardButton('🔙 Назад', callback_data='ref')
to_profile = InlineKeyboardButton('🔙 Назад', callback_data='profile')
to_stats = InlineKeyboardButton('🔙 Назад', callback_data='stats')
to_tops = InlineKeyboardButton('🔙 Назад', callback_data='tops')
to_vip = InlineKeyboardButton('🔙 Назад', callback_data='vip')
to_lobby = InlineKeyboardButton('🔙 Назад', callback_data='lobby')

to_main_kb = InlineKeyboardMarkup().add(to_main)
to_ref_kb = InlineKeyboardMarkup().add(to_ref)
to_tops_kb = InlineKeyboardMarkup().add(to_tops)
to_lobby_kb = InlineKeyboardMarkup().add(to_lobby)

# Отмена ===============================================================================================================
cancel_search = InlineKeyboardButton('🚫 Отменить поиск', callback_data='cancel_search')
cancel_search_kb = InlineKeyboardMarkup().add(cancel_search)


# Лобби ================================================================================================================
rules = InlineKeyboardButton('Правила 📖', callback_data='rules')
registrate = InlineKeyboardButton('Регистрация ✍️', callback_data='registrate')
lobby_kb = InlineKeyboardMarkup().row(rules, registrate)


# Главное меню =========================================================================================================
search_man = InlineKeyboardButton('Найти ♂️', callback_data='search_man')
search = InlineKeyboardButton('Рандом 🔀', callback_data='search')
search_woman = InlineKeyboardButton('Найти ♀️', callback_data='search_woman')
vip = InlineKeyboardButton('Вип 👑', callback_data='vip')
ref = InlineKeyboardButton('Рефералка 💼', callback_data='ref')
profile = InlineKeyboardButton('Профиль 👤', callback_data='profile')
main_kb = InlineKeyboardMarkup().row(search_man, search, search_woman).row(vip, ref, profile)


# Профиль ==============================================================================================================
settings = InlineKeyboardButton('⚙️ Настройки', callback_data='settings')
stats = InlineKeyboardButton('📈 Статистика', callback_data='stats')
profile_kb = InlineKeyboardMarkup().add(settings).add(stats).add(to_main)


# Настройки  ===========================================================================================================
name = InlineKeyboardButton('🅰️ Имя', callback_data='name')
age = InlineKeyboardButton('🔞 Возраст', callback_data='age')
sex = InlineKeyboardButton('👫 Пол', callback_data='sex')
settings_kb = InlineKeyboardMarkup().add(name).add(age).add(sex).add(to_profile)


# Рефералка ============================================================================================================
def ref_kb(flag: bool):
    trade = InlineKeyboardButton('Обменять 💎', callback_data='trade')
    on = InlineKeyboardButton('Включить уведомления 🔔', callback_data='on')
    off = InlineKeyboardButton('Выключить уведомления 🔕', callback_data='off')
    if flag:
        return InlineKeyboardMarkup().add(trade).add(off).add(to_main)
    else:
        return InlineKeyboardMarkup().add(trade).add(on).add(to_main)


# Статистика ===========================================================================================================
top = InlineKeyboardButton('🏆 Рейтинги', callback_data='tops')
statistic_kb = InlineKeyboardMarkup().add(top).add(to_profile)


# Топы =================================================================================================================
top_messages = InlineKeyboardButton('🔝 Топ 5 по сообщениям', callback_data='top_messages')
top_likes = InlineKeyboardButton('🔝 Топ 5 по лайкам', callback_data='top_likes')
top_refs = InlineKeyboardButton('🔝 Топ 5 по рефам', callback_data='top_refs')
top_kb = InlineKeyboardMarkup().add(top_messages).add(top_likes).add(top_refs).add(to_stats)


# Вип ==================================================================================================================
free_vip = InlineKeyboardButton('🆓 Получить вип бесплатно', callback_data='ref')
buy_vip = InlineKeyboardButton('💰 Купить/Продлить вип', callback_data='buy_vip')
vip_kb = InlineKeyboardMarkup().add(free_vip).add(buy_vip).add(to_main)


# Покупка випа =========================================================================================================
day = InlineKeyboardButton('👑 Вип на день - 20₽', callback_data='vip_day')
week = InlineKeyboardButton('👑 Вип на неделю - 100₽', callback_data='vip_week')
month = InlineKeyboardButton('👑 Вип на месяц - 300₽', callback_data='vip_month')
buy_kb = InlineKeyboardMarkup().add(day).add(week).add(month).add(to_vip)


# Пол ==================================================================================================================
male = InlineKeyboardButton('Мужской ♂️', callback_data='male')
female = InlineKeyboardButton('Женский ♀️', callback_data='female')
sex_kb = InlineKeyboardMarkup().row(male, female)


# Оценка ===============================================================================================================
like = InlineKeyboardButton('👍 Лайк', callback_data='like')
dislike = InlineKeyboardButton('👎 Дизлайк', callback_data='dislike')
next_dialog = InlineKeyboardButton('➡️ Следующий диалог', callback_data='search')
search_kb = InlineKeyboardMarkup().row(like, dislike).add(next_dialog).add(to_main)
review_kb = InlineKeyboardMarkup().add(next_dialog).add(to_main)
