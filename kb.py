from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Назад ================================================================================================================
to_main = InlineKeyboardButton(text='🔙 На главную', callback_data='to_main')
to_ref = InlineKeyboardButton(text='🔙 Назад', callback_data='ref')
to_profile = InlineKeyboardButton(text='🔙 Назад', callback_data='profile')
to_settings = InlineKeyboardButton(text='🔙 Назад', callback_data='settings')
to_stats = InlineKeyboardButton(text='🔙 Назад', callback_data='stats')
to_tops = InlineKeyboardButton(text='🔙 Назад', callback_data='tops')
to_vip = InlineKeyboardButton(text='🔙 Назад', callback_data='vip')
to_lobby = InlineKeyboardButton(text='🔙 Назад', callback_data='lobby')
to_buy = InlineKeyboardButton(text='🔙 Назад', callback_data='buy_vip')


to_main_kb = InlineKeyboardBuilder().add(to_main).as_markup()
to_ref_kb = InlineKeyboardBuilder().add(to_ref).as_markup()
to_settings_kb = InlineKeyboardBuilder().add(to_settings).as_markup()
to_tops_kb = InlineKeyboardBuilder().add(to_tops).as_markup()
to_lobby_kb = InlineKeyboardBuilder().add(to_lobby).as_markup()
to_buy_kb = InlineKeyboardBuilder().add(to_buy).as_markup()


# Отмена ===============================================================================================================
cancel_search = InlineKeyboardButton(text='🚫 Отменить поиск', callback_data='cancel_search')
cancel_search_kb = InlineKeyboardBuilder().add(cancel_search).as_markup()


# Лобби ================================================================================================================
rules = InlineKeyboardButton(text='Правила 📖', callback_data='rules')
registrate = InlineKeyboardButton(text='Регистрация ✍️', callback_data='registrate')
lobby_kb = InlineKeyboardBuilder().row(rules, registrate).as_markup()


# Главное меню =========================================================================================================
search_man = InlineKeyboardButton(text='Найти ♂️', callback_data='search_man')
search = InlineKeyboardButton(text='Рандом 🔀', callback_data='search')
search_woman = InlineKeyboardButton(text='Найти ♀️', callback_data='search_woman')
vip = InlineKeyboardButton(text='Вип 👑', callback_data='vip')
ref = InlineKeyboardButton(text='Рефералка 💼', callback_data='ref')
profile = InlineKeyboardButton(text='Профиль 👤', callback_data='profile')
main_kb = InlineKeyboardBuilder().row(search_man, search, search_woman).row(vip, ref, profile).as_markup()


# Профиль ==============================================================================================================
settings = InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')
stats = InlineKeyboardButton(text='📈 Статистика', callback_data='stats')
profile_kb = InlineKeyboardBuilder().add(settings).add(stats).add(to_main).adjust(1).as_markup()


# Настройки  ===========================================================================================================
name = InlineKeyboardButton(text='🅰️ Имя', callback_data='name')
age = InlineKeyboardButton(text='🔞 Возраст', callback_data='age')
sex = InlineKeyboardButton(text='👫 Пол', callback_data='sex')
settings_kb = InlineKeyboardBuilder().add(name).add(age).add(sex).add(to_profile).adjust(1).as_markup()


# Рефералка ============================================================================================================
def ref_kb(flag: bool):
    trade = InlineKeyboardButton(text='Обменять 💎', callback_data='trade')
    on = InlineKeyboardButton(text='Включить уведомления 🔔', callback_data='on')
    off = InlineKeyboardButton(text='Выключить уведомления 🔕', callback_data='off')
    if flag:
        return InlineKeyboardBuilder().add(trade).add(off).add(to_main).adjust(1).as_markup()
    else:
        return InlineKeyboardBuilder().add(trade).add(on).add(to_main).adjust(1).as_markup()


# Статистика ===========================================================================================================
top = InlineKeyboardButton(text='🏆 Рейтинги', callback_data='tops')
statistic_kb = InlineKeyboardBuilder().add(top).add(to_profile).adjust(1).as_markup()


# Топы =================================================================================================================
top_messages = InlineKeyboardButton(text='🔝 Топ 5 по сообщениям', callback_data='top_messages')
top_likes = InlineKeyboardButton(text='🔝 Топ 5 по лайкам', callback_data='top_likes')
top_refs = InlineKeyboardButton(text='🔝 Топ 5 по рефам', callback_data='top_refs')
top_kb = InlineKeyboardBuilder().add(top_messages).add(top_likes).add(top_refs).add(to_stats).adjust(1).as_markup()


# Вип ==================================================================================================================
free_vip = InlineKeyboardButton(text='🆓 Получить вип бесплатно', callback_data='ref')
buy_vip = InlineKeyboardButton(text='💰 Купить/Продлить вип', callback_data='buy_vip')
vip_kb = InlineKeyboardBuilder().add(free_vip).add(buy_vip).add(to_main).adjust(1).as_markup()


# Покупка випа =========================================================================================================
day = InlineKeyboardButton(text='👑 Вип на день - 20₽', callback_data='vip_day')
week = InlineKeyboardButton(text='👑 Вип на неделю - 100₽', callback_data='vip_week')
month = InlineKeyboardButton(text='👑 Вип на месяц - 300₽', callback_data='vip_month')
buy_kb = InlineKeyboardBuilder().add(day).add(week).add(month).add(to_vip).adjust(1).as_markup()


# Пол ==================================================================================================================
male = InlineKeyboardButton(text='Мужской ♂️', callback_data='male')
female = InlineKeyboardButton(text='Женский ♀️', callback_data='female')
sex_kb = InlineKeyboardBuilder().row(male, female).as_markup()


# Оценка ===============================================================================================================
like = InlineKeyboardButton(text='👍 Лайк', callback_data='like')
dislike = InlineKeyboardButton(text='👎 Дизлайк', callback_data='dislike')
next_dialog = InlineKeyboardButton(text='➡️ Следующий диалог', callback_data='search')
search_kb = InlineKeyboardBuilder().row(like, dislike).row(next_dialog).row(to_main).as_markup()
review_kb = InlineKeyboardBuilder().add(next_dialog).add(to_main).adjust(1).as_markup()

# Поиск по полу без випа ===============================================================================================
sex_search_no_vip_kb = InlineKeyboardBuilder().add(buy_vip, to_main).adjust(1).as_markup()
