import sqlite3

def create_tables_user(user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(
        f'CREATE TABLE IF NOT EXISTS users_data (id int,name text, surname text,patronymik text,city text,phone_number text,info text,tovar text,key text)')
    conn.commit()
    cur.close()
    conn.close()

    conn = sqlite3.connect('database/ZAKAZI_HISTORY.sql')
    cur = conn.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS zakazi (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id int ,zakaz text)')
    conn.commit()
    cur.close()
    conn.close()

    conn = sqlite3.connect(f'database/CORZINA_USERS.sql')
    cur = conn.cursor()
    cur.execute(f'CREATE TABLE IF NOT EXISTS corzina_{user_id} (description text)')
    conn.commit()
    cur.close()
    conn.close()

def proverka(user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM users_data WHERE id = "{user_id}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def insert_fio(id,fio):
    data = str(fio).split(',')
    name = data[0]
    lastname = data[1]
    patronymik = data[2]

    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(
        f'INSERT INTO users_data (id,name,surname,patronymik) VALUES ("{id}","{name}","{lastname}","{patronymik}")')
    conn.commit()
    cur.close()
    conn.close()

def inser_city(id,city):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET city = ? WHERE id = ?', (city, id))
    conn.commit()
    cur.close()
    conn.close()


def get_phone_number(id,phone_number):
    if (len(phone_number) == 11) and (phone_number[0:2] == '89' or (phone_number[0:2] == '79')):

        conn = sqlite3.connect('database/Users.sql')
        cur = conn.cursor()
        cur.execute(f'UPDATE users_data SET phone_number = ? WHERE id = ?',(phone_number,id))
        conn.commit()
        cur.close()
        conn.close()

        return True
    else:
        return False

def get_user_info(id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM users_data WHERE id = "{id}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_corzina_data(id):
    conn = sqlite3.connect('database/CORZINA_USERS.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM corzina_{id}')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def indert_zakaz_into_table(id,Zakaz):
    conn = sqlite3.connect('database/ZAKAZI_HISTORY.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO zakazi (user_id,zakaz) VALUES  (?,?)', (id, Zakaz))
    conn.commit()
    cur.execute(f'SELECT id FROM zakazi WHERE user_id = ? AND zakaz = ?', (id, Zakaz))
    zakaz_id = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return zakaz_id

def clear_coezina(id):
    conn = sqlite3.connect('database/CORZINA_USERS.sql')
    cur = conn.cursor()
    cur.execute(f'DELETE FROM corzina_{id}')
    conn.commit()
    cur.close()
    conn.close()

def get_razdel(SQL_name,table_name):
    conn = sqlite3.connect(f'database/{SQL_name}')
    cur = conn.cursor()
    cur.execute(f'SELECT name_razdel FROM {table_name}')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def update_name_razdel(razdeli_new_str,user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET info = ? WHERE id = ?', (razdeli_new_str, user_id))
    conn.commit()
    cur.close()
    conn.close()

def select_info_from_user_data(user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT info FROM users_data WHERE id = "{user_id}"')
    info_str = cur.fetchall()
    cur.close()
    conn.close()
    return info_str

def choice_name_razdel(sql_name,table_name):
    conn = sqlite3.connect(f'database/{sql_name}')
    cur = conn.cursor()
    cur.execute(f'SELECT name_razdel FROM {table_name}')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_info_razdel(sql_name,table_name,name_razdel):
    conn = sqlite3.connect(f'database/{sql_name}')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM {table_name} WHERE name_razdel = ?', (name_razdel,))
    info = cur.fetchall()
    cur.close()
    conn.close()
    return info

def update_userdata_info_key(info_str,key,user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET info = ? WHERE id = ?', (info_str, user_id))
    cur.execute(f'UPDATE users_data SET key = ? WHERE id = ?', (key, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_tovar_info(user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT info FROM users_data WHERE id = "{user_id}"')
    info_str = cur.fetchall()
    cur.execute(f'SELECT key FROM users_data WHERE id = "{user_id}"')
    key_str = cur.fetchall()
    cur.close()
    conn.close()
    return key_str,info_str

def set_tovar(elem_str,user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET tovar = ? WHERE id = ?',(elem_str,user_id))
    conn.commit()
    cur.close()
    conn.close()

def select_tovar_from_user_data(user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT tovar FROM users_data WHERE id = "{user_id}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def insert_tovar_into_corzina(user_id,description):
    conn = sqlite3.connect('database/CORZINA_USERS.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO corzina_{user_id} (description) VALUES ("{description}")')
    conn.commit()
    cur.close()
    conn.close()

def select_all_from_history(user_id):
    conn = sqlite3.connect('database/ZAKAZI_HISTORY.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM zakazi WHERE user_id = "{user_id}"')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def povtor_zakaz(user_id,zakaz):
    conn = sqlite3.connect('database/ZAKAZI_HISTORY.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO zakazi (user_id,zakaz) VALUES  (?,?)', (user_id, zakaz[2]))
    conn.commit()
    cur.execute(f'SELECT id FROM zakazi WHERE user_id = ? AND zakaz = ? ORDER BY id DESC LIMIT 1', (user_id, zakaz[2]))
    zakaz_id = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return zakaz_id

def update_user_fio(name,surname,patronymik,user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET name = ?,surname = ?,patronymik = ? WHERE id = ?',
                (name, surname, patronymik, user_id))
    conn.commit()
    cur.close()
    conn.close()

def update_user_city(new_city_new,user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET city = ? WHERE id = ?', (new_city_new, user_id))
    conn.commit()
    cur.close()
    conn.close()

def update_phone_number(new_phone_number,user_id):
    conn = sqlite3.connect('database/Users.sql')
    cur = conn.cursor()
    cur.execute(f'UPDATE users_data SET phone_number = ? WHERE id = ?', (new_phone_number, user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_photo_id_by_name(photo_name):
    conn = sqlite3.connect('database/IMAGES_IDS.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM image_id WHERE name = ?',(photo_name,))
    data = cur.fetchall()
    if data == []:
        cur.execute(f'SELECT id FROM image_id WHERE name = ?',('нет_фото.jpg',))
        data = cur.fetchall()
        return data[0][0]

    else:
        return data[0][1]