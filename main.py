import telebot
from telebot import types
import sqlite3
from datetime import datetime

bot = telebot.TeleBot('6931176961:AAHA-BQVWqfddpY9JvROJQHbi0Fx6DtYM9A') #токен


#добавление базы данных
dt = sqlite3.connect('salon.db', check_same_thread=False)
cursor = dt.cursor()

def record_create():
    # Создание таблицы для записей
    cursor.execute("""CREATE TABLE IF NOT EXISTS record (
        date text,
        service text,
        master text,
        visitor text
    )""")

def create_usertable():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        userId text,
        name text)""")


def insert_record(date, service, master, visitor='-'):
    # Добавление записи
    cursor.execute("INSERT INTO record (date, service, master, visitor) VALUES (?, ?, ?, ?)", (date, service, master, visitor))
    dt.commit()

def update_visitor(date, service, master, visitor):
    cursor = dt.cursor()
    # Поле visitor меняем на данные пользователя
    cursor.execute("SELECT rowid FROM record WHERE date = ? AND service = ? AND master = ? AND visitor = '-'",
                   (date, service, master))
    alt = cursor.fetchone()
    cursor.execute("UPDATE record SET visitor = ? WHERE rowid = ?",
                   (visitor, alt[0]))
    cursor.execute("SELECT * FROM record")
    print(cursor.fetchall())
    dt.commit()

def pay_record(date, service, master, visitor):
    # Добавление информации о записи на услугу в таблицу
    date_today = datetime.now().date()
    cursor.execute("INSERT INTO pay (date_today, date, service, master, visitor) VALUES (?, ?, ?, ?, ?)", (date_today, date, service, master, visitor))
    dt.commit()

def record_show(date):
    cursor = dt.cursor()
   # Вывод записи
    cursor.execute("SELECT DISTINCT service, master FROM record WHERE date = ?", (date,))
    rows = cursor.fetchall()
    rasp_list = []
    for row in rows:
        service, master = row
        rasp_list.append(f" Услуга {service}, специалист: {master}")
    return rasp_list

# Удаление данных
# cursor.execute("DELETE FROM record")

# Удаление таблицы
# cursor.execute("DROP TABLE record")

"""
insert_record('10.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('20.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('24.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('26.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('10.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('20.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('24.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('26.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('10.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('20.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('26.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('10.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('20.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('24.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
"""

record_create()
create_usertable()

# Вывод таблицы с записью
cursor.execute("SELECT * FROM record")
print(cursor.fetchall())



# Вывод таблицы с оплаченными занятиями
cursor.execute("SELECT * FROM pay")
print(cursor.fetchall())

dt.commit()




@bot.message_handler(commands=['start']) #декоратор, обрабатываем команду старт
def start(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    botton1 = types.KeyboardButton('Записаться')
    botton2 = types.KeyboardButton('Отменить запись')
    markup.add(botton1, botton2)
    botton4 = types.InlineKeyboardButton('Перейти на сайт', url='https://nataxtare.github.io/sweet_lemon_site/')

    botton5 = types.KeyboardButton('Прайс')
    markup.add(botton4, botton5)
    bot.send_message(call.chat.id, f'Здравствуйте, {call.from_user.first_name}! \nВас приветствует салон красоты Sweety Lemon.', reply_markup=markup)

    ids = cursor.execute("""SELECT userId FROM user""").fetchall()
    if (str(call.chat.id),) not in ids:
        bot.send_message(call.chat.id,
                         'Перед тем, как начать пользоваться ботом, пожалуйста, укажите свои полные фамилию, имя и отчество.')
        bot.register_next_step_handler(call, new_name)



@bot.message_handler(content_types=['text'])
def menu(call):
    if call.text == 'Записаться':
        markup = types.InlineKeyboardMarkup()
        cursor.execute("SELECT DISTINCT date FROM record")
        dates_ = cursor.fetchall()
        dates = []
        for date in dates_:
            for d in date:
                dates.append(d)
        for date in dates:
            butt = 'date:' + date
            print(butt)
            button = types.InlineKeyboardButton(date, callback_data=butt)
            markup.add(button)
        bot.send_message(call.chat.id, 'Выберите день:', reply_markup=markup)

    if call.text == 'Отменить запись':
        visitor = cursor.execute("SELECT name FROM user WHERE userId = ?", (call.chat.id,)).fetchone()[0]
        cursor.execute("SELECT date, service FROM record WHERE visitor = ?", (visitor,))
        markup = types.InlineKeyboardMarkup()
        dates_serv_ = cursor.fetchall()
        dates_serv = []
        for d_n in dates_serv_:
            dates_serv.append(d_n)
        print(dates_serv)
        for d_n in dates_serv:
            date = d_n[0]
            service = d_n[1]
            butt = 'date_serv:' + date + ':' + service
            name_butt = date + ' ' + service
            button = types.InlineKeyboardButton(name_butt, callback_data=butt)
            markup.add(button)
        bot.send_message(call.chat.id, 'Какую услугу хотите отменить?', reply_markup=markup)

    if call.text == 'Прайс':
        photo = open('price.jpg', 'rb')
        bot.send_photo(call.chat.id, photo, caption='Вот наш прайс:')
    if call.text == 'Перейти на сайт':
        bot.send_message(call.chat.id, 'https://nataxtare.github.io/sweet_lemon_site/')


@bot.callback_query_handler(func=lambda callback: 'date_serv:' in callback.data)
def callback_cancel(callback):

    date_serv = callback.data.split(':')
    date = date_serv[1]
    service = date_serv[2]
    cursor.execute("SELECT master FROM record WHERE date = ? AND service = ?", (date, service))
    master = ''.join(cursor.fetchone())
    cursor.execute("UPDATE record SET visitor = '-' WHERE date = ? AND service = ? AND master = ?",
                   (date, service, master))
    dt.commit()
    bot.send_message(callback.message.chat.id, f'Запись на {date}, "{service}" успешно отменена.')
    cursor.execute("SELECT * FROM record")
    print(cursor.fetchall())


@bot.callback_query_handler(func=lambda callback: 'date:' in callback.data)
def callback_dates_show(callback):
    markup = types.InlineKeyboardMarkup()
    date = callback.data.split(':')[1]
    rasp_list = record_show(date)
    rasp_str = f'Информация об услугах на {date}:\n\n'
    for string in rasp_list:
        rasp_str += string
        rasp_str += '\n'
    rasp_str += '\nВыберите услугу, на которую хотели бы записаться:'
    for i in rasp_list:
        service = i.split(':')[0][1:].split(',')[0]
        reg = 'reg:' + date + ':' + service
        button = types.InlineKeyboardButton(service, callback_data=reg)
        markup.add(button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: 'reg:' in callback.data)
def callback_reg(callback):
    data_parts = callback.data.split(':')
    print(data_parts)
    date = data_parts[1]
    service = data_parts[2][7:]
    name = cursor.execute("SELECT name FROM user WHERE userId = ?", (callback.message.chat.id,)).fetchone()[0]
    cursor.execute('UPDATE record SET visitor = ? WHERE service = ? and date = ?', (name, service, date))
    dt.commit()

    bot.send_message(callback.message.chat.id, f'Вы успешно записаны {date} на {service}')

@bot.callback_query_handler(func=lambda callback: True)
def tt(callback):
    if callback.data == 'price':
        file = open('./price.jpg', 'rb')
        bot.send_photo(callback.message.chat.id, file)

def new_name(message):

    name = message.text
    cursor.execute("""INSERT INTO user(userId, name) VALUES (?, ?)""", (message.chat.id, name))
    dt.commit()
    bot.send_message(message.chat.id, 'Ваше имя успешно сохранено.')


bot.polling(none_stop=True)  # вызываем команду, благодаря которой бот работает непрерывно.