from aiogram import types

def create_main_buttons_user():
    markup = types.ReplyKeyboardMarkup(keyboard=[],resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Личный кабинет 👤')
    markup.keyboard.append([btn1])
    btn2 = types.KeyboardButton(text='Каталог 🛍')
    btn3 = types.KeyboardButton(text='Корзина 🛒')
    markup.keyboard.append([btn2,btn3])
    btn4 = types.KeyboardButton(text='Поддержка 🧑‍💻')
    btn5 = types.KeyboardButton(text='О нас 📌')
    markup.keyboard.append([btn4,btn5])

    return markup

def send_phone_number():
    markup = types.ReplyKeyboardMarkup(keyboard=[],resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Поделиться ☎️', request_contact=True)
    markup.keyboard.append([btn1])

    return markup

def kabinet_buttons(id):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='История заказов', callback_data=f'История {id}')
    markup.inline_keyboard.append([btn1])
    btn2 = types.InlineKeyboardButton(text='Изменить данные', callback_data=f'Изменить {id}')
    markup.inline_keyboard.append([btn2])
    return markup

def corzina_buttons():
    markup_main = types.ReplyKeyboardMarkup(keyboard=[],resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Оформить заказ')
    btn2 = types.KeyboardButton(text='Назад')
    markup_main.keyboard.append([btn1,btn2])
    return markup_main


def catalog_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Емкости наземные', callback_data='Раздел Емкости наземные')
    markup.inline_keyboard.append([btn1])
    btn2 = types.InlineKeyboardButton(text='Емкости подземные', callback_data='Раздел Емкости подземные')
    markup.inline_keyboard.append([btn2])
    btn3 = types.InlineKeyboardButton(text='Для дачи', callback_data='Раздел Для дачи')
    markup.inline_keyboard.append([btn3])
    btn4 = types.InlineKeyboardButton(text='Комплектующие', callback_data='Раздел Комплектующие')
    markup.inline_keyboard.append([btn4])
    btn5 = types.InlineKeyboardButton(text='Мусоросбросы', callback_data='Раздел Мусоросбросы')
    markup.inline_keyboard.append([btn5])
    btn6 = types.InlineKeyboardButton(text='Ящики', callback_data='Раздел ящики')
    markup.inline_keyboard.append([btn6])
    btn7 = types.InlineKeyboardButton(text='Мини АЗС', callback_data='Раздел АЗС')
    markup.inline_keyboard.append([btn7])
    btn8 = types.InlineKeyboardButton(text='Запчати для АЗС', callback_data='Раздел Запчасти АЗС')
    markup.inline_keyboard.append([btn8])
    return markup

def tanks_sklad_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Мытищи', callback_data='Корзина Емкости Мыт')
    btn2 = types.InlineKeyboardButton(text='Орехово-Зуево', callback_data='Корзина Емкости Орех')
    markup.inline_keyboard.append([btn1,btn2])
    return markup

def dacha_sklad_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Мытищи', callback_data='Корзина дача Мыт')
    btn2 = types.InlineKeyboardButton(text='Орехово-Зуево', callback_data='Корзина дача Орех')
    markup.inline_keyboard.append([btn1,btn2])
    return markup

def kompl_skald_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Мытищи', callback_data='Корзина компл Мыт')
    btn2 = types.InlineKeyboardButton(text='Орехово-Зуево', callback_data='Корзина компл Орех')
    markup.inline_keyboard.append([btn1,btn2])
    return markup

def corzina_musor_button():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Добавить в корзину', callback_data='Корзина мусор')
    markup.inline_keyboard.append([btn1])
    return markup

def boxes_sklad_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Мытищи', callback_data='Корзина короб Мыт')
    btn2 = types.InlineKeyboardButton(text='Орехово-Зуево', callback_data='Корзина короб Орех')
    markup.inline_keyboard.append([btn1,btn2])
    return markup

def AZS_sklad_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='PIUSI', callback_data='Корзина АЗС PIUSI')
    btn2 = types.InlineKeyboardButton(text='БелАк', callback_data='Корзина АЗС БелАк')
    markup.inline_keyboard.append([btn1,btn2])
    btn3 = types.InlineKeyboardButton(text='Китай премиум', callback_data='Корзина АЗС Кит_прем')
    btn4 = types.InlineKeyboardButton(text='Китай', callback_data='Корзина АЗС китай')
    markup.inline_keyboard.append([btn3,btn4])
    return markup

def corzina_zap_azs():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Добавить в корзину', callback_data='Корзина зап_азс')
    markup.inline_keyboard.append([btn])
    return markup

def povtor_zakaz_buttons(index):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Повторить заказ', callback_data=f'Повторить заказ {index}')
    markup.inline_keyboard.append([btn])
    return markup

def rechange_user_data_buttons(user_id):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='ФИО', callback_data=f'ФИО {user_id}')
    markup.inline_keyboard.append([btn1])
    btn2 = types.InlineKeyboardButton(text='Город', callback_data=f'Город {user_id}')
    markup.inline_keyboard.append([btn2])
    btn3 = types.InlineKeyboardButton(text='Номер телефона', callback_data=f'Номер телефона {user_id}')
    markup.inline_keyboard.append([btn3])
    return markup

