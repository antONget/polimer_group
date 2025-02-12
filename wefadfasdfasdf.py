from aiogram import Bot,types,Dispatcher,F
from aiogram.filters import Command,StateFilter,or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import  default_state,State,StatesGroup
from aiogram.types import FSInputFile

import time
import sqlite3

Token = '7661034756:AAFUgia-2Vco7Vx7MJHnak_rSL9JsCr_fGA'

bot = Bot(Token)
dp = Dispatcher(bot=bot)

@dp.message(Command('start'))
async def load_photo(message: types.Message):
    names_main = []

    conn = sqlite3.connect('database/IMAGES_IDS.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS image_id (name str,id str)')
    conn.commit()
    cur.close()
    cur.close()

    conn = sqlite3.connect('database/GROUND_TANKS.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT image_name FROM ground_tanks')
    names = cur.fetchall()
    cur.close()
    conn.close()
    names_set = list(set(names))
    for name in names_set:
        names_main.append(name)
        print(123123)

    conn = sqlite3.connect('database/BOXES.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT image_name FROM boxes')
    names = cur.fetchall()
    cur.close()
    conn.close()
    names_set = list(set(names))
    for name in names_set:
        names_main.append(name)
        print(123123)

    conn = sqlite3.connect('database/FOR_TRASH.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT image_name FROM for_trash')
    names = cur.fetchall()
    cur.close()
    conn.close()
    names_set = list(set(names))
    for name in names_set:
        names_main.append(name)
        print(123123)

    conn = sqlite3.connect('database/FOR_COUNTRY.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT image_name FROM for_village')
    names = cur.fetchall()
    cur.close()
    conn.close()
    names_set = list(set(names))
    for name in names_set:
        names_main.append(name)
        print(123123)

    conn = sqlite3.connect('database/ACCESSORIES.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT image_name FROM accessories')
    names = cur.fetchall()
    cur.close()
    conn.close()
    names_set = list(set(names))
    for name in names_set:
        names_main.append(name)
        print(123123)

    conn = sqlite3.connect('database/UNDERGROUND_TANKS.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT image_name FROM underground_tanks')
    names = cur.fetchall()
    cur.close()
    conn.close()
    names_set = list(set(names))
    for name in names_set:
        names_main.append(name)
        print(123123)


    conn = sqlite3.connect('database/IMAGES_IDS.sql')
    cur = conn.cursor()
    for photo_name in names_main:
        time.sleep(0.5)
        if str(photo_name[0]) == 'None':
            continue
        else:
            photo = FSInputFile(f'img/{photo_name[0]}')
            sent_photo = await bot.send_photo(chat_id=message.chat.id,photo=photo)
            photo_id = str(sent_photo.photo[-1].file_id)
            print(photo_name[0])
            cur.execute('INSERT INTO image_id (name,id) VALUES (?,?)',(str(photo_name[0]),photo_id))
            conn.commit()

    cur.close()
    conn.close()

    await message.answer('готово')

@dp.message(Command('photo'))
async def get_id(message: types.Message):
    photo_name = 'нет_фото.jpg'
    conn = sqlite3.connect('database/IMAGES_IDS.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM image_id WHERE name = ?',(photo_name,))
    id = cur.fetchall()

    print(id[0][1])
if __name__ == '__main__':
    dp.run_polling(bot)
