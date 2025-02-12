import logging
from aiogram import Bot,types,Dispatcher,F,Router
from aiogram.filters import Command,StateFilter,or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import  default_state,State,StatesGroup
from aiogram.types import FSInputFile


import time
import sqlite3
from collections import OrderedDict
import os

from config_data.config import Config,load_config
from keyboards import admin_keyboards,user_keyboards
from database import requests_user,request_admin

config:Config = load_config()

admin_id = config.tg_bot.admin_ids.split(',')
manager_id = config.tg_bot.manager_ids.split(',')

photo_name = ''
my_dict = {"Ем_наз":['TOVARI.sql','ground_tanks'],
           "Ем_подз":['TOVARI.sql','underground_tanks'],
           "Дача":['TOVARI.sql','for_village'],
           "Компл":['TOVARI.sql','accessories'],
           "Мусор":['TOVARI.sql','for_trash'],
           "Короб":['TOVARI.sql','Boxes'],
           "Азс":['TOVARI.sql','azs'],
           "Зап_азс":['TOVARI.sql','azs_parts']
           }

logging.basicConfig(level=logging.INFO,
                    # filename="py_log.log",
                    # filemode='w',
                    format='%(filename)s:%(lineno)d #%(levelname)-8s '
                           '[%(asctime)s] - %(name)s - %(message)s')

class FSMFillForm(StatesGroup):
    fill_fio = State()
    fill_phone_number = State()
    fill_city = State()
    change_fio = State()
    change_city = State()
    change_phone_number = State()


    change_photo_admin_name = State()
    change_photo_admin_photo = State()
    add_photo_admin_name = State()
    add_photo_admin_photo = State()


bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot=bot)
# dp.include_router(error.router)

@dp.message(Command('start'),StateFilter(default_state))
async def start (message: types.Message,state:FSMContext):
    user_id = message.from_user.id
    logging.info('start')

    requests_user.create_tables_user(user_id)

    if str(message.from_user.id) in admin_id:
        await message.answer('Вы администратор')
        await main_buttons_admin(message)
    else:
        user_id = message.from_user.id

        data = requests_user.proverka(user_id)

        if data:
            name = message.from_user.first_name
            await message.answer(f'Добрый день {name}, рады вас видеть снова в нашем магазине.')
            await main_buttons_user(message)

        else:

            await message.answer('Доброго времени суток, рады вас видеть в нашем магазине. '
                                         'Компания «Полимер-Групп» производит и реализует емкости для воды пластиковые, '
                                         'которые, как показывает практика, пользуются большой популярностью благодаря очень '
                                         'высокому качеству и доступной стоимости. Тара из пластика широко используется для перевозки'
                                         ' и хранения питьевой и технической воды во многих отраслях.')
            time.sleep(4)
            await  message.answer('Скажите как мы можем к вам обращаться?\nВведите ваше ФИО в таком формате: "Фамилия,Имя,Отчество"')
            await state.set_state(FSMFillForm.fill_fio)

@dp.message(Command('photo'))
async def rechange_photo_for_new_bot(message: types.Message):
    logging.info('rechange_photo_for_new_bot')

    photo_list = request_admin.rechange_photo_id_for_new_bot()

    conn = sqlite3.connect('database/IMAGES_IDS.sql')
    cur = conn.cursor()
    for photo_name in photo_list:
        time.sleep(0.5)
        if str(photo_name[0]) == 'None':
            continue
        else:
            photo = FSInputFile(f'img/{photo_name[0]}')
            sent_photo = await bot.send_photo(chat_id=message.chat.id, photo=photo)
            photo_id = sent_photo.photo[-1].file_id

            cur.execute('INSERT INTO image_id (name,id) VALUES (?,?)', (str(photo_name[0]), photo_id))
            conn.commit()

    photo = FSInputFile('нет_фото.jpg')
    sent_photo = await bot.send_photo(chat_id=message.chat.id, photo=photo)
    photo_id = sent_photo.photo[-1].file_id
    cur.execute('INSERT INTO image_id (name,id) VALUES (?,?)', (str('нет_фото.jpg'), photo_id))
    conn.commit()

    cur.close()
    conn.close()

    await message.answer('готово')

#ПОЛУЧЕНИЕ ДАННЫХ ОТ ПОЛЬЗОВАТЕЛЯ

#ПОЛУЧЕНИЕ ФИО
@dp.message(StateFilter(FSMFillForm.fill_fio))
async def get_fio(message: types.Message,state:FSMContext):
    logging.info('get_fio')
    fio = message.text
    id = message.from_user.id
    try:
        requests_user.insert_fio(id,fio)
        await message.answer('Из какого вы города?')
        await state.set_state(FSMFillForm.fill_city)
    except Exception as e:
        await message.answer('Неправильный формат ввода,попробуйте еще раз')
        await state.set_state(FSMFillForm.fill_fio)

#ПОЛУЧЕНИЕ ГОРОДА
@dp.message(StateFilter(FSMFillForm.fill_city))
async def get_city (message: types.Message,state:FSMContext):
    logging.info('get_city')
    markup = user_keyboards.send_phone_number()

    city = message.text
    id = message.from_user.id

    requests_user.inser_city(id,city)

    await message.answer('Укажите ваш номер телефона воспользовавшись кнопкой "Поделиться ☎️" расположенной рядом с клавиатурой 👇',reply_markup=markup)
    await state.set_state(FSMFillForm.fill_phone_number)

#ПОЛУЧЕНИЕ НОМЕРА ТЕЛЕФОНА И ЕГО ПРОВЕРКА
@dp.message(StateFilter(FSMFillForm.fill_phone_number))
async def get_phone_numder(message: types.Message,state:FSMContext):
    logging.info('get_phone_number')
    id = message.from_user.id
    try:
        phone_number = str(message.contact.phone_number)
        if requests_user.get_phone_number(id,phone_number):
            await message.answer('Благодарим вас за регистрацию')
            await state.clear()
            await main_buttons_user(message)

        else:
            await message.answer('Некоректный формат номера,повторите пожалуйста ввод вручуню')
            await state.set_state(FSMFillForm.fill_phone_number)
    except Exception as e:
        phone_number = str(message.text)
        if requests_user.get_phone_number(id, phone_number):
            await message.answer('Благодарим вас за регистрацию')
            await state.clear()
            await main_buttons_user(message)

        else:
            await message.answer('Некоректный формат номера,повторите пожалуйста ввод вручуню')
            await state.set_state(FSMFillForm.fill_phone_number)

@dp.message(F.text == '123132')
async def main_buttons_admin(message: types.Message):
    logging.info('main_buttons_admin')
    request_admin.create_tables()
    markup = admin_keyboards.create_keyboard_admin()
    await message.answer('Вы являетесь администратором,выберите действие',reply_markup=markup)

@dp.message(or_f((F.text == 'Загрузить файл'),(F.text == 'Загрузить фотографию'),(F.text == 'Обновить фотографию')))
async def main_admin_photo(message: types.Message,state:FSMContext):
    logging.info('main_admin_photo')
    if message.text == 'Загрузить фотографию':
        await message.answer('Введите название фотографии, в соотвествии с данными из таблицы')
        await state.set_state(FSMFillForm.add_photo_admin_name)
    if message.text == 'Загрузить файл':
        await message.answer('Отправьте файл')
    if message.text == 'Обновить фотографию':
        await message.answer('Введите название фото, которое хотите обновить (Вводить в соответствии с данными из таблицы')
        await state.set_state(FSMFillForm.change_photo_admin_name)


@dp.message(F.document)
async def get_file(message: types.Message):
    await message.answer('Ожидайте, файл загружается, это может занять пару минут')
    logging.info('get_file')

    file_id = message.document.file_id
    file_name = message.document.file_name

    file = await bot.get_file(file_id)

    await bot.download_file(file.file_path,f'{file_name}')

    request_admin.process_excel_file(file_name)

    os.remove(file_name)

    await message.answer('Файл успешно загружен')

@dp.message(StateFilter(FSMFillForm.change_photo_admin_name))
async def re_get_photo_name(message: types.Message,state:FSMContext):
    logging.info('re_get_photo_name')
    photo_name = message.text
    names = request_admin.get_all_photo_name()
    for name in names:
        if str(name[0]) == str(photo_name):
            await state.set_state(FSMFillForm.change_photo_admin_photo)
            break
    else:
        await message.answer('Совпадений не найдено,нажмите на кнопку и попробуйте еще раз')
        await state.clear()

@dp.message(StateFilter(FSMFillForm.change_photo_admin_photo))
async def re_get_photo(message: types.Message,state:FSMContext):
    logging.info('re_get_photo')
    photo_id = message.photo[-1].file_id

    request_admin.rechange_photo_id(photo_name,photo_id)

    await message.answer('Фото обновлено!')
    await state.clear()


@dp.message(StateFilter(FSMFillForm.add_photo_admin_name))
async def get_photo_name(message: types.Message,state:FSMContext):
    logging.info('get_photo_name')
    global photo_name
    photo_name = message.text
    await message.answer('Отправьте фотографию')
    await state.set_state(FSMFillForm.add_photo_admin_photo)

@dp.message(StateFilter(FSMFillForm.add_photo_admin_photo))
async def get_photo(message: types.Message,state:FSMContext):
    logging.info('get_photo')
    file_id = message.photo[-1].file_id
    print(file_id)

    request_admin.get_photo_to_sqlite(f'{photo_name}.jpg',file_id)

    await message.answer('Фото сохранено')
    await state.clear()

@dp.message(F.text == 'Назад')
async def main_buttons_user (message: types.Message):
    logging.info('main_buttons_user')
    markup = user_keyboards.create_main_buttons_user()
    await message.answer('Выберите раздел,кнопки расположены рядом с клавиатурой 👇',reply_markup=markup)


@dp.message(or_f((F.text == 'Личный кабинет 👤') , (F.text == 'Назад') , (F.text == 'Оформить заказ') ,(F.text == 'Корзина 🛒') , (F.text == 'Поддержка 🧑‍💻') , (F.text == 'О нас 📌') , (F.text == 'Каталог 🛍')))
async def main_user(message: types.Message):
    logging.info('main_user')
    id = message.from_user.id
    if message.text == 'Личный кабинет 👤':

        markup = user_keyboards.kabinet_buttons(id)

        data = requests_user.get_user_info(id)

        name = data[0][1]
        lastname = data[0][2]
        patronymik = data[0][3]
        city = data[0][4]
        phone_numder = data[0][5]

        sent_message =  await message.answer(f'Ваши данные: \n'
                                         f'Имя: {name} \n'
                                         f'Фамилия: {lastname} \n'
                                         f'Отчество: {patronymik} \n'
                                         f'Город: {city} \n'
                                         f'Номер телефона: {phone_numder}',reply_markup=markup)

        message_id = sent_message.message_id
        requests_user.update_name_razdel(message_id,id)

    if message.text == 'Назад':
        await main_buttons_user(message)

    if message.text == 'Оформить заказ':
        data = requests_user.get_corzina_data(id)

        corzina = list(OrderedDict.fromkeys(data))

        final_cost = 0

        Zakaz = '\n'

        for tovar in corzina:
            cost = int(tovar[0].split('Цена:')[-1][:-2])
            cnt = data.count(tovar)

            final_cost+=(cost*cnt)



            tovar_str = f'{tovar[0]}\nКол-вл: {cnt}шт \nЦена за {cnt}шт - {cnt*cost}\n\n\n'
            Zakaz+=tovar_str

        Zakaz+= f'Сумма заказа: {final_cost} Р'

        await message.answer('Благодаримм вас за оформление заказа,в скором времени мы с вами свяжемся')

        zakaz_id = requests_user.indert_zakaz_into_table(id,Zakaz)

        requests_user.clear_coezina(id)

        for manager in manager_id:
            print(manager)
            await bot.send_message(manager,f'Клиент: tg://user?id={id} \nНомер заказа: {zakaz_id} \n\n{Zakaz}')

        requests_user.clear_coezina(id)

    if message.text == 'Корзина 🛒':
        markup_main = user_keyboards.corzina_buttons()

        data = requests_user.get_corzina_data(id)

        if data == []:
            await message.answer('Корзина пуста')

        else:

            await message.answer('Ваша корзина:',reply_markup=markup_main)

            corzina = list(OrderedDict.fromkeys(data))

            for tovar in corzina:
                try:
                    cost = int(tovar[0].split('Цена:')[-1][:-2])
                except ValueError as e:
                    cost = 0

                cnt = data.count(tovar)

                calback = corzina.index(tovar)
                markup = user_keyboards.create_buttons_corzina_start(calback)

                await message.answer(f'Товар 1/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt} шт\nЦена за {cnt}шт - {cnt * cost} Руб.',reply_markup=markup)

                break

    if message.text == 'Поддержка 🧑‍💻':
        await message.answer('Здесь будет ссылка на поддержку')

    if message.text == 'О нас 📌':
        await message.answer('Здесь будет отображаться информация о компании')

    if message.text == 'Каталог 🛍':
        markup = user_keyboards.catalog_buttons()
        await message.answer('Выберите раздел:',reply_markup=markup)

@dp.callback_query(or_f(F.data.startswith('back_corzina_'),(F.data.startswith('forward_corzina_'))))
async def pagination_corzina(callback: types.callback_query):
    user_id = callback.from_user.id
    data = requests_user.get_corzina_data(user_id)
    corzina = list(OrderedDict.fromkeys(data))

    for tovar in corzina:
        if callback.data == f'forward_corzina_{corzina.index(tovar)}':
            try:
                cost = int(tovar[0].split('Цена:')[-1][:-2])
            except ValueError as e:
                cost = 0

            cnt = data.count(tovar)
            if tovar == corzina[-1]:
                markup = user_keyboards.create_buttons_corzina_next_page(True,corzina.index(tovar))

                await callback.message.edit_text(text=
                    f'Товар {corzina.index(tovar)+1}/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt} шт\nЦена за {cnt}шт - {cnt * cost} Руб.',
                    reply_markup=markup)

                break

            else:
                markup = user_keyboards.create_buttons_corzina_next_page(False,corzina.index(tovar))

                await callback.message.edit_text(text=
                                                 f'Товар {corzina.index(tovar)+1}/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt} шт\nЦена за {cnt}шт - {cnt * cost} Руб.',
                                                 reply_markup=markup)

                break

        if callback.data == f'back_corzina_{corzina.index(tovar)}':
            try:
                cost = int(tovar[0].split('Цена:')[-1][:-2])
            except ValueError as e:
                cost = 0
            cnt = data.count(tovar)
            if tovar == corzina[0]:
                markup = user_keyboards.create_buttons_corzina_back_page(True,corzina.index(tovar))

                await callback.message.edit_text(text=
                    f'Товар {corzina.index(tovar)+1}/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt} шт\nЦена за {cnt}шт - {cnt * cost} Руб.',
                    reply_markup=markup)

                break

            else:
                markup = user_keyboards.create_buttons_corzina_back_page(False,corzina.index(tovar))

                await callback.message.edit_text(text=
                                                 f'Товар {corzina.index(tovar)+1}/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt} шт\nЦена за {cnt}шт - {cnt * cost} Руб.',
                                                 reply_markup=markup)

                break


@dp.callback_query(or_f((F.data.startswith('+1,')) , (F.data.startswith('-1,')) , (F.data.startswith('Удалить,'))))
async def corzina_plus_minus(callback: types.callback_query):
    logging.info('corzina_plus_minus')
    user_id = callback.from_user.id

    conn = sqlite3.connect('database/CORZINA_USERS.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM corzina_{user_id}')
    data_old = cur.fetchall()

    corzina = list(OrderedDict.fromkeys(data_old))

    for tovar in corzina:
        if callback.data == f'-1,{corzina.index(tovar)}':

            cost = int(tovar[0].split('Цена:')[-1][:-2])
            cnt = data_old.count(tovar)

            cur.execute(f'DELETE FROM corzina_{user_id} WHERE rowid = (SELECT MAX(rowid) FROM corzina_{user_id} WHERE description = "{tovar[0]}") ')
            conn.commit()
            cur.execute(f'SELECT * FROM corzina_{user_id}')
            data_old = cur.fetchall()

            corzina = list(OrderedDict.fromkeys(data_old))

            index = corzina.index(tovar)

            if tovar == corzina[-1]:
                markup = user_keyboards.create_buttons_corzina_next_page(True, index)

            elif tovar == corzina[0]:
                markup = user_keyboards.create_buttons_corzina_back_page(True,index)

            else:
                markup = user_keyboards.create_buttons_corzina_next_page(False, index)

            await callback.message.edit_text(f'Товар {corzina.index(tovar)+1}/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt-1} шт\nЦена за {cnt-1}шт - {cnt * cost} Руб.',reply_markup=markup)

            break

        if callback.data == f'+1,{corzina.index(tovar)}':
            cost = int(tovar[0].split('Цена:')[-1][:-2])
            cnt = data_old.count(tovar)

            cur.execute(f'INSERT INTO corzina_{user_id} (description) VALUES ("{tovar[0]}")')
            conn.commit()
            cur.execute(f'SELECT * FROM corzina_{user_id}')
            data_old = cur.fetchall()

            corzina = list(OrderedDict.fromkeys(data_old))

            index = corzina.index(tovar)

            if tovar == corzina[-1]:
                markup = user_keyboards.create_buttons_corzina_next_page(True,index)
            elif tovar == corzina[0]:
                markup = user_keyboards.create_buttons_corzina_back_page(True,index)
            else:
                markup = user_keyboards.create_buttons_corzina_next_page(False,index)

            await callback.message.edit_text( f'Товар {corzina.index(tovar)+1}/{len(corzina)}\n\n{tovar[0]}\n\nКол-во: {cnt+1} шт\nЦена за {cnt+1}шт - {cnt * cost} Руб.',reply_markup=markup)

        if callback.data == f'Удалить,{corzina.index(tovar)}':
            print(123123)
            index = corzina.index(tovar)

            if tovar == corzina[0]:
                markup = user_keyboards.button_for_deleted_tovar(True,index)
                await callback.message.edit_text(f'Товар {corzina.index(tovar) + 1}/{len(corzina)}\n\nТовар удален',
                                                 reply_markup=markup)

            elif tovar == corzina[-1]:
                markup = user_keyboards.button_for_deleted_tovar(False,index)
                await callback.message.edit_text(f'Товар {corzina.index(tovar) + 1}/{len(corzina)}\n\nТовар удален',
                                                 reply_markup=markup)
            else:
                markup = user_keyboards.button_for_deleted_tovar(False, index)
                await callback.message.edit_text(f'Товар {corzina.index(tovar) + 1}/{len(corzina)}\n\nТовар удален',
                                                 reply_markup=markup)


            cur.execute(f'DELETE FROM corzina_{user_id} WHERE description = "{tovar[0]}"')
            conn.commit()

            corzina.remove(tovar)
            print(corzina)

            if corzina == []:
                await callback.message.edit_text(f'Ваша корзина пуста',reply_markup=user_keyboards.empty_keyboard())


    cur.close()
    conn.close()


@dp.callback_query(F.data.startswith('Раздел'))
async def buttons_razdel(callback: types.CallbackQuery):
    logging.info('buttons_razdel')
    user_id = callback.from_user.id


    SQL_name = 'TOVARI.sql'
    table_name = ''
    description = ''

    if callback.data == 'Раздел Емкости наземные':
        table_name = 'ground_tanks'
        description = 'Ем_наз'

    if callback.data == 'Раздел Емкости подземные':
        table_name = 'underground_tanks'
        description = 'Ем_подз'

    if callback.data == 'Раздел Для дачи':
        table_name = 'for_village'
        description = 'Дача'

    if callback.data == 'Раздел Комплектующие':
        table_name = 'accessories'
        description = 'Компл'

    if callback.data == 'Раздел Мусоросбросы':
        table_name = 'for_trash'
        description = 'Мусор'
    if callback.data == 'Раздел ящики':
        table_name = 'Boxes'
        description = 'Короб'
    if callback.data == 'Раздел АЗС':
        table_name = 'azs'
        description = 'Азс'
    if callback.data == 'Раздел Запчасти АЗС':
        table_name = 'azs_parts'
        description = 'Зап_азс'

    data = requests_user.get_razdel(SQL_name,table_name)

    razdeli = []

    for elem in data:
        razdeli.append(elem[0])

    razdeli_new = []
    for elem in razdeli:
        if elem not in razdeli_new:
            razdeli_new.append(elem)

    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    cnt = 0

    razdeli_new_str = '[' + str(razdeli_new) + ',' + str([description]) + ']'
    requests_user.update_name_razdel(razdeli_new_str,user_id)

    for razdel in razdeli_new:
        if cnt <8:
            cnt+=1
            btn = types.InlineKeyboardButton(text=f'{razdel}',callback_data=f'{description},{razdeli_new.index(razdel)}')
            markup.inline_keyboard.append([btn])
        if cnt == 8:
            btn1 = types.InlineKeyboardButton(text='>>>',callback_data='forward razdel 2')
            markup.inline_keyboard.append([btn1])
            await callback.message.edit_text('Выберите раздел:', reply_markup=markup)
            break

    if cnt == 1:
        name_razdel = ''
        key = description

        table_name = my_dict[key][1]
        sql_name = my_dict[key][0]

        index = 0
        data = requests_user.choice_name_razdel(sql_name, table_name)

        razdeli = []

        for elem in data:
            razdeli.append(elem[0])

        razdeli_new = []
        for elem in razdeli:
            if elem not in razdeli_new:
                razdeli_new.append(elem)

        for razdel in razdeli_new:
            if razdeli_new.index(razdel) == index:
                name_razdel = razdel

        info = requests_user.get_info_razdel(sql_name, table_name, name_razdel)

        info_str = str(info)

        requests_user.update_userdata_info_key(info_str, key, user_id)

        markup = types.InlineKeyboardMarkup(inline_keyboard=[])
        cnt = 0
        cnt_pages = int(len(info) / 5) + 1
        for elem in info:
            if cnt < 5:
                btn = types.InlineKeyboardButton(text=f'{elem[1]}', callback_data=f'Товар:{elem[-1]}')
                markup.inline_keyboard.append([btn])
                cnt += 1
            if cnt == 5:
                btn2 = types.InlineKeyboardButton(text='>>>', callback_data='forward 2')
                markup.inline_keyboard.append([btn2])
                await callback.message.edit_text(text=f'{elem[0]}\n\nСтраница 1/{cnt_pages}', reply_markup=markup)
                break
        else:
            await callback.message.edit_text(text=f'{info[0][0]}',reply_markup=markup)

    else:
        await callback.message.edit_text(text='Выберите раздел',reply_markup=markup)


@dp.callback_query(or_f(F.data.startswith('forward razdel') , F.data.startswith('back razdel')))
async def pagination_razdel(callback: types.CallbackQuery):
    logging.info('pagination_razdel')
    user_id = callback.from_user.id
    info_str = requests_user.select_info_from_user_data(user_id)

    razdeli_list = eval(info_str[0][0])
    razdeli = razdeli_list[0]
    description = razdeli_list[-1][0]
    cnt_pages = int(len(razdeli) / 5) +1
    for i in range(cnt_pages+1):

        if callback.data == f'forward razdel {i}':
            markup = types.InlineKeyboardMarkup(inline_keyboard=[])
            cnt = 0
            page = i-1
            for elem in razdeli[8*page:]:
                if cnt<8:
                    btn = types.InlineKeyboardButton(text=f'{elem}',callback_data=f'{description},{razdeli.index(elem)}')
                    markup.inline_keyboard.append([btn])
                if cnt == 8:
                    btn1 = types.InlineKeyboardButton(text='>>>', callback_data=f'forward razdel {i+1}')
                    btn2 = types.InlineKeyboardButton(text='<<<',callback_data=f'back razdel {i}')
                    markup.inline_keyboard.append([btn1,btn2])
                    await callback.message.edit_text(f'Выберите раздел', reply_markup=markup)
                    break
            else:
                btn_back = types.InlineKeyboardButton(text='<<<',callback_data=f'back razdel {i}')
                markup.inline_keyboard.append([btn_back])
                await callback.message.edit_text(f'Выберите раздел', reply_markup=markup)

        if callback.data == f'back razdel {i}':
            markup = types.InlineKeyboardMarkup(inline_keyboard=[])
            cnt = 0
            page_start = i-2
            page_end = i-1
            for elem in razdeli[page_start*8:8*page_end]:
                if cnt<8:
                    btn = types.InlineKeyboardButton(text=f'{elem}',callback_data=f'{description},{razdeli.index(elem)}')
                    markup.inline_keyboard.append([btn])
                    cnt+=1
                if cnt == 8 and page_start == 0:
                    btn_forward = types.InlineKeyboardButton(text='>>>',callback_data=f'forward razdel {i}')
                    markup.inline_keyboard.append([btn_forward])
                    await callback.message.edit_text(f'Выберите раздел', reply_markup=markup)
                    break
                if cnt == 8 and page_start!=0:
                    btn_back = types.InlineKeyboardButton(text='<<<',callback_data=f'back razdel {i+1}')
                    btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'forward razdel {i + 1}')
                    markup.inline_keyboard.append([btn_back,btn_forward])
                    await callback.message.edit_text(f'Выберите раздел:', reply_markup=markup)
                    break



@dp.callback_query(lambda F:any(F.data.startswith(key) for key in my_dict.keys()))
async def tovari(callback: types.CallbackQuery):
    logging.info('tovari')
    user_id = callback.from_user.id
    for key in my_dict.keys():
        if key in callback.data:
            name_razdel = ''

            table_name = my_dict[key][1]
            sql_name = my_dict[key][0]

            index = int(str(callback.data).split(',')[1])
            data = requests_user.choice_name_razdel(sql_name,table_name)

            razdeli = []

            for elem in data:
                razdeli.append(elem[0])

            razdeli_new = []
            for elem in razdeli:
                if elem not in razdeli_new:
                    razdeli_new.append(elem)

            for razdel in razdeli_new:
                if razdeli_new.index(razdel) == index:
                    name_razdel = razdel

            info = requests_user.get_info_razdel(sql_name,table_name,name_razdel)

            info_str = str(info)

            requests_user.update_userdata_info_key(info_str,key,user_id)

            markup = types.InlineKeyboardMarkup(inline_keyboard=[])
            cnt = 0
            cnt_pages = int(len(info)/5) + 1
            for elem in info:
                if cnt<5:
                    btn = types.InlineKeyboardButton(text=f'{elem[1]}',callback_data=f'Товар:{elem[-1]}')
                    markup.inline_keyboard.append([btn])
                    cnt+=1
                if cnt == 5:
                    btn2 = types.InlineKeyboardButton(text='>>>',callback_data='forward 2')
                    markup.inline_keyboard.append([btn2])
                    await callback.message.edit_text(text=f'{elem[0]}\n\nСтраница 1/{cnt_pages}', reply_markup=markup)
                    break
            else:
                await callback.message.edit_text(text=f'{info[0][0]}:', reply_markup=markup)

@dp.callback_query(or_f(F.data.startswith('back'),F.data.startswith('forward')))
async def pagination(callback: types.CallbackQuery):
    logging.info('pagination')
    user_id = callback.from_user.id

    info_str = requests_user.select_info_from_user_data(user_id)

    info = eval(info_str[0][0])

    cnt_pages = int(len(info) / 5) + 1
    for i in range(cnt_pages + 1):
        if callback.data == f'forward {i}':
            markup = types.InlineKeyboardMarkup(inline_keyboard=[])
            cnt = 0
            page = i-1
            for elem in info[5*page:]:
                if cnt<5:
                    btn = types.InlineKeyboardButton(text=f'{elem[1]}',callback_data=f'Товар:{elem[-1]}')
                    markup.inline_keyboard.append([btn])
                    cnt+=1
                if cnt == 5:
                    btn_back = types.InlineKeyboardButton(text='<<<',callback_data=f'back {i}')
                    btn_forward = types.InlineKeyboardButton(text='>>>',callback_data=f'forward {i+1}')
                    markup.inline_keyboard.append([btn_back,btn_forward])
                    await callback.message.edit_text(f'{elem[0]}\n\nСтраница: {i}/{cnt_pages}', reply_markup=markup)
                    break
            else:
                btn_back = types.InlineKeyboardButton(text='<<<',callback_data=f'back {i}')
                markup.inline_keyboard.append([btn_back])
                await callback.message.edit_text(f'{elem[0]}\n\nСтраница: {i}/{cnt_pages}', reply_markup=markup)

        if callback.data == f'back {i}':
            markup_2 = types.InlineKeyboardMarkup(inline_keyboard=[])
            cnt = 0
            page_start = i-2
            page_end = i-1
            for elem in info[page_start*5:5*page_end]:
                if cnt < 5:
                    btn = types.InlineKeyboardButton(text=f'{elem[1]}', callback_data=f'Товар:{elem[-1]}')
                    markup_2.inline_keyboard.append([btn])
                    cnt += 1
                if cnt == 5 and page_start == 0:
                    btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'forward {i + 1}')
                    markup_2.inline_keyboard.append([btn_forward])
                    await callback.message.edit_text(f'{elem[0]}\n\nСтраница: {i-1}/{cnt_pages}', reply_markup=markup_2)
                    break

                if cnt == 5 and page_start!= 0:
                    btn_back = types.InlineKeyboardButton(text='<<<',callback_data=f'back {i-1}')
                    btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'forward {i + 1}')
                    markup_2.inline_keyboard.append([btn_back,btn_forward])
                    await callback.message.edit_text(f'{elem[0]}\n\nСтраница: {i-1}/{cnt_pages}', reply_markup=markup_2)
                    break

@dp.callback_query(F.data.startswith('Товар:'))
async def choice_tovar(callback: types.CallbackQuery):
    logging.info('choice_tovar')
    user_id = callback.from_user.id

    key_str,info_str = requests_user.get_tovar_info(user_id)

    key = key_str[0][0]
    info = eval(info_str[0][0])

    if key == 'Ем_наз' or key == 'Ем_подз':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':

                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                art = elem[2]
                size = elem[3]
                weight = elem[4]
                volume = elem[5]
                cost_mitichi = elem[6]
                cost_zuevo = elem[7]

                photo = requests_user.get_photo_id_by_name(f'{elem[8]}')
                print(photo)


                markup = user_keyboards.tanks_sklad_buttons()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)
                await bot.send_photo(chat_id=callback.from_user.id,photo=photo,caption=f'Название: {name} \n\n'
                                                                            f'Артикул: {art} \n\n'
                                                                            f'Размер: {size} \n\n'
                                                                            f'Вес: {weight} КГ \n\n'
                                                                            f'Обьем: {volume} \n\n'
                                                                            f'Цена склад Мытищи: {cost_mitichi} Р \n\n'
                                                                            f'Цена склад Орехово-зуево: {cost_zuevo} Р \n\n'
                                                                            f'* Цвет на фотографии может отличаться \n\n'
                                                                          f'Чтобы добавить товар в корзину нажмите на кнопку с названием склада',reply_markup=markup)

    if key == 'Дача':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':
                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                art = elem[2]
                size = elem[3]
                weight = elem[4]
                cost_mitichi = elem[5]
                cost_zuevo = elem[6]

                photo = requests_user.get_photo_id_by_name(f'{elem[8]}')

                markup = user_keyboards.dacha_sklad_buttons()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)
                await bot.send_photo(chat_id=callback.from_user.id,photo=photo,caption=f'Название: {name} \n\n'
                                                                            f'Артикул: {art} \n\n'
                                                                            f'Размер: {size} \n\n'
                                                                            f'Вес: {weight} КГ\n\n'
                                                                            f'Цена склад Мытищи: {cost_mitichi} Р \n\n'
                                                                            f'Цена склад Орехово-зуево: {cost_zuevo} Р \n\n'
                                                                            f'* Цвет на фотографии может отличаться \n\n'
                                                                          f'Чтобы добавить товар в корзину нажмите на кнопку с названием склада',reply_markup=markup)

    if key == 'Компл':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':
                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                art = elem[2]
                cost_mitichi = elem[3]
                cost_zuevo = elem[4]

                photo = requests_user.get_photo_id_by_name(f'{elem[5]}')


                markup = user_keyboards.kompl_skald_buttons()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)
                await bot.send_photo(chat_id=callback.from_user.id,photo=photo,caption=f'Название: {name} \n\n'
                                                                            f'Артикул: {art} \n\n'
                                                                            f'Цена склад Мытищи: {cost_mitichi} P \n\n'
                                                                            f'Цена склад Орехово-зуево: {cost_zuevo} P \n\n'
                                                                            f'* Цвет на фотографии может отличаться \n\n'
                                                                          f'Чтобы добавить товар в корзину нажмите на кнопку с названием склада',reply_markup=markup)

    if key == 'Мусор':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':
                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                art = elem[2]
                haract = elem[3]
                weight = elem[4]
                cost_mitichi = elem[5]

                photo = requests_user.get_photo_id_by_name(f'{elem[6]}')

                markup = user_keyboards.corzina_musor_button()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)
                await bot.send_photo(chat_id=callback.from_user.id,photo=photo,caption=f'Название: {name} \n\n'
                                                                            f'Артикул: {art} \n\n'
                                                                            f'Характеристики: {haract} \n\n'
                                                                            f'Вес: {weight} КГ\n\n'
                                                                            f'Цена склад Мытищи: {cost_mitichi} Р \n\n'
                                                                            f'* Цвет на фотографии может отличаться \n\n',reply_markup=markup)

    if key == 'Короб':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':
                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                art = elem[2]
                obiem = elem[3]
                size = elem[4]
                weight = elem[5]
                cost_mitichi = elem[6]
                cost_zuevo = elem[7]

                photo = requests_user.get_photo_id_by_name(f'{elem[8]}')

                markup = user_keyboards.boxes_sklad_buttons()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)
                await bot.send_photo(chat_id=callback.from_user.id,photo=photo,caption=f'Название: {name} \n\n'
                                                                            f'Артикул: {art} \n\n'
                                                                            f'Обьем: {obiem} Л \n\n'
                                                                            f'Размер: {size} \n\n'
                                                                            f'Вес: {weight} КГ \n\n'
                                                                            f'Цена склад Мытищи: {cost_mitichi} Р \n\n'
                                                                            f'Цена склад Орехово-зуево: {cost_zuevo} Р \n\n'
                                                                            f'* Цвет на фотографии может отличаться \n\n'
                                                                          f'Чтобы добавить товар в корзину нажмите на кнопку с названием склада',reply_markup=markup)

    if key == 'Азс':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':
                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                obiem = elem[2]
                size = elem[3]
                art_PIUSU = elem[4]
                cost_PIUSI = elem[5]
                art_BelAk = elem[6]
                cost_BelAk = elem[7]
                art_china_premium = elem[8]
                cost_china_premium = elem[9]
                art_china = elem[10]
                cost_china = elem[11]
                markup = user_keyboards.AZS_sklad_buttons()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)


                await callback.message.answer(f'Название: {name} \n\n'
                                                                f'Обьем: {obiem} Л \n\n'
                                                                f'Размер: {size} \n\n'
                                                                f'Артикул PUISI: {art_PIUSU} \n'
                                                                f'Цена PIUSI: {cost_PIUSI} Р\n\n'
                                                                f'Артикул БелАк: {art_BelAk} \n'
                                                                f'Цена БелАк: {cost_BelAk} Р\n\n'
                                                                f'Артикул Китай Премиум: {art_china_premium} \n'
                                                                f'Цена Китай Премиум: {cost_china_premium} Р \n\n'
                                                                f'Артикул Китай :{art_china} \n'
                                                                f'Цена Китай: {cost_china} Р\n\n'
                                                                f'Чтобы добавить товар в корзину нажмите на кнопку с названием склада',reply_markup=markup)
    if key == 'Зап_азс':
        for elem in info:
            if callback.data == f'Товар:{elem[-1]}':
                elem_str = str(elem)

                requests_user.set_tovar(elem_str,user_id)

                name = elem[1]
                art = elem[2]
                cost = elem[3]
                markup = user_keyboards.corzina_zap_azs()
                await bot.delete_message(callback.from_user.id,callback.message.message_id)
                await callback.message.answer(f'Название: {name} \n\n'
                                                                f'Артикул: {art} \n\n'
                                                                f'Цена: {cost} Л \n\n',reply_markup=markup)

@dp.callback_query(F.data.startswith('Корзина '))
async def add_to_corzina(callback: types.CallbackQuery):
    logging.info('add_to_corzina')
    user_id = callback.from_user.id

    data = requests_user.select_tovar_from_user_data(user_id)

    tovar = eval(data[0][0])
    if callback.data == 'Корзина Емкости Мыт':
        description = f'Товар: {tovar[1]}\nАртикул: {tovar[2]}\nРазмер: {tovar[3]} \nВес: {tovar[4]} КГ\nОбьем: {tovar[5]} Л \nЦена: {tovar[6]} Р'
        if str(tovar[6]) != 'None' and str(tovar[6]) != 'скоро' and str(tovar[6] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id,description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Мытищи')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина Емкости Орех':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nРазмер: {tovar[3]} \nВес: {tovar[4]} КГ\nОбьем: {tovar[5]} Л \nЦена: {tovar[7]} Р'
        if str(tovar[7]) != 'None' and str(tovar[7]) != 'скоро' and str(tovar[7] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Орехово-Зуево')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина дача Мыт':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nРазмер: {tovar[3]} \nВес: {tovar[4]} КГ\nЦена: {tovar[5]} Р'
        if str(tovar[5]) != 'None'and str(tovar[5]) != 'скоро' and str(tovar[5] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Мытищи')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина дача Орех':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nРазмер: {tovar[3]} \nВес: {tovar[4]} КГ\nЦена: {tovar[6]} Р'
        if str(tovar[6]) != 'None' and str(tovar[6]) != 'скоро' and str(tovar[6] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Орехово-Зуево')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина компл Мыт':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nЦена: {tovar[3]} Р'
        if str(tovar[3]) != 'None' and str(tovar[3]) != 'скоро' and str(tovar[3] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Мытищи')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина компл Орех':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nЦена: {tovar[4]} Р'
        if str(tovar[4]) != 'None' and str(tovar[4]) != 'скоро' and str(tovar[4] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Орехово-Зуево')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина мусор':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nХарактеристики:{tovar[3]}\nВес: {tovar[4]} КГ\nЦена: {tovar[5]} Р'
        if str(tovar[5]) != 'None' and str(tovar[5]) != 'скоро' or str(tovar[5] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину')
        else:
            await callback.message.answer('Выбранного вами товара нет на складе')

    if callback.data == 'Корзина короб Мыт':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nОбьем: {tovar[3]} Л\nРазмер: {tovar[4]}\nВес: {tovar[5]} КГ\nЦена: {tovar[6]} Р'
        if str(tovar[6]) != 'None' and str(tovar[6]) != 'скоро' and str(tovar[6] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Мытищи')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина короб Орех':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nОбьем: {tovar[3]} Л\nРазмер: {tovar[4]}\nВес: {tovar[5]} КГ\nЦена: {tovar[7]} Р'
        if str(tovar[7]) != 'None' and str(tovar[7]) != 'скоро' and str(tovar[7] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину со склада Орехово-Зуево')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина АЗС PIUSI':
        description = f'Товар: {tovar[1]} \nОбьем: {tovar[2]} Л\nРазмер: {tovar[3]}\nАртикул: {tovar[4]}\nЦена: {tovar[5]} Р'
        if str(tovar[5]) != 'None' and str(tovar[5]) != 'скоро' and str(tovar[5] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина АЗС БелАк':
        description = f'Товар: {tovar[1]} \nОбьем: {tovar[2]} Л\nРазмер: {tovar[3]}\nАртикул: {tovar[6]}\nЦена: {tovar[7]} Р'
        if str(tovar[7]) != 'None' and str(tovar[7]) != 'скоро' and str(tovar[7] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина АЗС Кит_прем':
        description = f'Товар: {tovar[1]} \nОбьем: {tovar[2]} Л\nРазмер: {tovar[3]}\nАртикул: {tovar[8]}\nЦена: {tovar[9]} Р'
        if str(tovar[9]) != 'None' and str(tovar[9]) != 'скоро' and str(tovar[9] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина АЗС китай':
        description = f'Товар: {tovar[1]} \nОбьем: {tovar[2]} Л\nРазмер: {tovar[3]}\nАртикул: {tovar[10]}\nЦена: {tovar[11]} Р'
        if str(tovar[11]) != 'None' and str(tovar[11]) != 'скоро' and str(tovar[11] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину')
        else:
            await callback.message.answer('Товара нет на выбранном вами складе,пожалуйста выберите другой склад')

    if callback.data == 'Корзина зап_азс':
        description = f'Товар: {tovar[1]} \nАртикул: {tovar[2]}\nЦена: {tovar[3]} Р'
        if str(tovar[3]) != 'None' and str(tovar[3]) != 'скоро' and str(tovar[3] != 'под заказ'):
            requests_user.insert_tovar_into_corzina(user_id, description)
            await callback.message.answer(f'Товар добавлен в корзину')
        else:
            await callback.message.answer('Выбранного вами товара нет на складе')



@dp.callback_query(or_f(F.data.startswith('История'),F.data.startswith('Изменить'),F.data.startswith('Повторить заказ')))
async def change_data_or_history (callback: types.CallbackQuery):
    logging.info('change_data_or_history')
    user_id = callback.from_user.id
    if 'Повторить заказ' in callback.data:
        data = requests_user.select_all_from_history(user_id)

        for zakaz in data:
            if callback.data == f'Повторить заказ {data.index(zakaz)}':
                zakaz_id = requests_user.povtor_zakaz(user_id,zakaz)

                await callback.message.answer('Благодарим вас за повторное оформление заказа,в скором времени мы с вами свяжемся')
                for manager in manager_id:
                    await bot.send_message(manager,f'Клиент: tg://user?id={user_id} \nНомер заказа: {zakaz_id} \n\n{zakaz[2]}')


    if callback.data == f'История {user_id}':

        data = requests_user.select_all_from_history(user_id)
        if data != []:
            await bot.delete_message(callback.from_user.id,callback.message.message_id)
            for zakaz in data:

                markup = user_keyboards.povtor_zakaz_buttons(data.index(zakaz))

                await callback.message.answer(f'Номер заказа: {zakaz[0]}'f'\n{zakaz[2]}',reply_markup=markup)
        else:
            await bot.delete_message(callback.from_user.id,callback.message.message_id)
            await callback.message.answer('Вы пока что не оформили ни одного заказа')

    if callback.data == f'Изменить {user_id}':

        markup = user_keyboards.rechange_user_data_buttons(user_id)
        await callback.message.answer('Какие данные вы хотите изменить?',reply_markup=markup)


@dp.callback_query(or_f(F.data.startswith('ФИО'),F.data.startswith('Город'),F.data.startswith('Номер телефона')))
async def change_data(callback: types.CallbackQuery,state:FSMContext):
    logging.info('change_data')
    user_id = callback.from_user.id
    data = requests_user.get_user_info(user_id)
    print(data)
    name = data[0][1]
    lastname = data[0][2]
    patronymik = data[0][3]
    city = data[0][4]
    phone_numder = data[0][5]

    if callback.data == f'ФИО {user_id}':
        await  callback.message.edit_text(text=f'Ваше текущее ФИО: {name},{lastname},{patronymik}\n\nВведите ФИО в таком формате через запятую: "Фамилия,Имя,Отчество"',reply_markup=user_keyboards.empty_keyboard())
        await state.set_state(FSMFillForm.change_fio)
    if callback.data == f'Город {user_id}':
        await callback.message.edit_text(text=f'Ваш текущий город: {city}\nВведите новое название города',reply_markup=user_keyboards.empty_keyboard())
        await state.set_state(FSMFillForm.change_city)
    if callback.data == f'Номер телефона {user_id}':
        await callback.message.edit_text(text=f'Ваш текущий номер телефона: {phone_numder}\nВведите новый номер телефона',reply_markup=user_keyboards.empty_keyboard())
        await state.set_state(FSMFillForm.change_phone_number)

@dp.message(StateFilter(FSMFillForm.change_fio))
async def get_new_fio(message: types.Message,state:FSMContext):
    logging.info('get_new_fio')
    user_id = message.from_user.id
    new_fio_old = str(message.text)
    try:
        message_id_in_list = (requests_user.select_info_from_user_data(user_id))
        message_id = int(message_id_in_list[0][0])

        new_fio_new = new_fio_old.split(',')
        name = new_fio_new[0]
        surname = new_fio_new[1]
        patronymik = new_fio_new[2]

        requests_user.update_user_fio(name, surname, patronymik, user_id)
        await state.clear()

        data = requests_user.get_user_info(user_id)
        print(data)
        city = data[0][4]
        phone_numder = data[0][5]

        new_data = (f'Ваши данные:\n'
                    f'Имя: {name}\n'
                    f'Фамилия: {surname}\n'
                    f'Отчество: {patronymik}\n'
                    f'Город: {city}\n'
                    f'Номер телефона: {phone_numder}')

        await message.edit_text(text=new_data,reply_markup=user_keyboards.kabinet_buttons(user_id))
        await bot.delete_message(message.from_user.id,message.message_id-1)
        await message.answer('Данные сохранены!')

    except Exception as e:
        await message.answer('Неправильный формат ввода данных,введите данные еще раз')
        await state.set_state(FSMFillForm.change_fio)

@dp.message(StateFilter(FSMFillForm.change_city))
async def get_new_city(message: types.Message,state:FSMContext):
    logging.info('get_new_city')
    user_id = message.from_user.id
    new_city_old = str(message.text)
    new_city_new = new_city_old

    requests_user.update_user_city(new_city_new,user_id)

    await state.clear()

    message_id_in_list = (requests_user.select_info_from_user_data(user_id))
    message_id = int(message_id_in_list[0][0])

    data = requests_user.get_user_info(user_id)
    name = data[0][1]
    lastname = data[0][2]
    patronymik = data[0][3]
    phone_numder = data[0][5]

    new_data = (f'Ваши данные:\n'
                f'Имя: {name}\n'
                f'Фамилия: {lastname}\n'
                f'Отчество: {patronymik}\n'
                f'Город: {new_city_new}\n'
                f'Номер телефона: {phone_numder}')

    await message.edit_text(text=new_data,reply_markup=user_keyboards.kabinet_buttons(user_id))

    await bot.delete_message(message.from_user.id, message.message_id - 1)
    await message.answer('Данные сохранены!')


@dp.message(StateFilter(FSMFillForm.change_phone_number))
async def get_new_phone_number(message: types.Message,state:FSMContext):
    logging.info('get_new_phone_number')
    user_id = message.from_user.id
    new_phone_number = str(message.text)

    if (len(new_phone_number) == 11) and (new_phone_number[0:2] == '89' or (new_phone_number[0:2] == '79')):
        requests_user.update_phone_number(new_phone_number,user_id)

        await state.clear()

        message_id_in_list = (requests_user.select_info_from_user_data(user_id))
        message_id = int(message_id_in_list[0][0])

        data = requests_user.get_user_info(user_id)
        name = data[0][1]
        lastname = data[0][2]
        patronymik = data[0][3]
        city = data[0][4]

        new_data = (f'Ваши данные:\n'
                    f'Имя: {name}\n'
                    f'Фамилия: {lastname}\n'
                    f'Отчество: {patronymik}\n'
                    f'Город: {city}\n'
                    f'Номер телефона: {new_phone_number}')

        await message.edit_text(text=new_data,reply_markup=user_keyboards.kabinet_buttons(user_id))

        await bot.delete_message(message.from_user.id, message.message_id - 1)
        await message.answer('Данные сохранены!')


    else:
        await message.answer('Неправильный формат номера телефона,попробуйте ввести еще раз')
        await state.set_state(FSMFillForm.change_phone_number)

if __name__ == "__main__":
    dp.run_polling(bot)