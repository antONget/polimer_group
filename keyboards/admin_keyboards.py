from aiogram import types
def create_keyboard_admin():
    markup = types.ReplyKeyboardMarkup(keyboard=[])

    btn1 = types.KeyboardButton(text='Загрузить файл')
    btn2 = types.KeyboardButton(text='Загрузить фотографию')

    markup.keyboard.append([btn1,btn2])

    return markup