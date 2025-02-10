from aiogram import types
def create_keyboard_admin():
    markup = types.ReplyKeyboardMarkup(keyboard=[],resize_keyboard=True)

    btn1 = types.KeyboardButton(text='Загрузить файл')
    btn2 = types.KeyboardButton(text='Загрузить фотографию')
    btn3 = types.KeyboardButton(text='Обновить фотографию')

    markup.keyboard.append([btn1,btn2])
    markup.keyboard.append([btn3])

    return markup