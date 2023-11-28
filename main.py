import telebot
import webbrowser
from telebot import types
import sqlite3
from datetime import datetime
from aiogram.types.web_app_info import WebAppInfo

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

def pay_create():
    # Создание таблицы пользователей, которые оплатили услугу
    cursor.execute("""CREATE TABLE IF NOT EXISTS pay_record (
            date_today text,
            date text,
            service text,
            master text,
            visitor text
        )""")

def insert_record(date, service, master, visitor='-'):
    # Добавление расписания
    cursor.execute("INSERT INTO record (date, service, master, visitor) VALUES (?, ?, ?, ?)", (date, service, master, visitor))
    dt.commit()

def update_visitor(date, service, master, visitor):
    cursor = dt.cursor()
    # Поле visitor меняем на данные пользователя
    cursor.execute("SELECT rowid FROM record WHERE date = ? AND service = ? AND master = ? AND visitor = '-'",
                   (date, service, master))
    row = cursor.fetchone()
    cursor.execute("UPDATE record SET visitor = ? WHERE rowid = ?",
                   (visitor, row[0]))
    cursor.execute("SELECT * FROM record")
    print(cursor.fetchall())
    dt.commit()

def pay_record(date, service, master, visitor):
    # Добавление информации о записи на услугу в таблицу
    date_today = datetime.now().date()
    cursor.execute("INSERT INTO pay_record (date_today, date, service, master, visitor) VALUES (?, ?, ?, ?, ?)", (date_today, date, service, master, visitor))
    dt.commit()

def record_show(date):
    cursor = dt.cursor()
   # Вывод записи
    cursor.execute("SELECT DISTINCT service, master FROM record WHERE date = ?", (date,))
    rows = cursor.fetchall()
    rasp_list = []
    for row in rows:
        service, master = row
        rasp_list.append(f"услуга{service}, специалист: {master}")
    return rasp_list

# Удаление данных
# cursor.execute("DELETE FROM record")

# Удаление таблицы
# cursor.execute("DROP TABLE record")

"""
insert_record('10.11.23', 'Стрижка', 'Петрова Анна Павловна')
insert_record('10.11.23', 'Стрижка', 'Петрова Анна Павловна')
insert_record('10.11.23', 'Стрижка', 'Петрова Анна Павловна')
insert_record('10.11.23', 'Стрижка', 'Петрова Анна Павловна')
insert_record('20.11.23', 'Укладка', 'Лукъянова Наталья Олеговна')
insert_record('20.11.23', 'Укладка', 'Лукъянова Наталья Олеговна')
insert_record('20.11.23', 'Укладка', 'Лукъянова Наталья Олеговна')
insert_record('20.11.23', 'Укладка', 'Лукъянова Наталья Олеговна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
"""

# Вывод таблицы с записью
cursor.execute("SELECT * FROM record")
print(cursor.fetchall())

# Вывод таблицы с оплаченными занятиями
#cursor.execute("SELECT * FROM pay_record")
#print(cursor.fetchall())

dt.commit()

name = ''

@bot.callback_query_handler(func=lambda callback: True)
def tt(callback):
    if callback.data == 'price':
        file = open('./price.jpeg', 'rb')
        bot.send_photo(callback.message.chat.id, file)

@bot.message_handler(commands=['start']) #декоратор, обрабатываем команду старт
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.KeyboardButton('Открыть веб приложение', web_app = WebAppInfo(url='https://supernatural-spn.net/episodes/6-sezon-11-seria/'))
    btn2 = types.InlineKeyboardButton('Прайс', callback_data='price')
    btn3 = types.KeyboardButton('Добавить окна для записи')
    btn4 = types.KeyboardButton('Отменить занятие')
    markup.row(btn1,btn2,btn3,btn4)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! \nВас приветствует салон красоты Sweety Lemon.', reply_markup=markup)
    if name == '':
        bot.send_message(message.chat.id,
                         'Для записи в салон, пожалуйста, укажите свои полные фамилию, имя и отчество')
        bot.register_next_step_handler(message, new_name)

@bot.message_handler(content_types=['text'])
def menu(message):

    if message.text == 'Записаться':
        markup = types.InlineKeyboardMarkup()
        cursor.execute("SELECT DISTINCT date FROM record")
        dates_ = cursor.fetchall()
        dates = []
        for date in dates_:
            for d in date:
                dates.append(d)
        for date in dates:
            butt = 'date:' + date
            button = types.InlineKeyboardButton(date, callback_data=butt)
            markup.add(button)
        bot.send_message(message.chat.id, 'Выберите день:', reply_markup=markup)
    elif message.text == 'Добавить места для записи':
        bot.send_message(message.chat.id, 'Введите сообщение в формате:\nгггг-мм-дд_Услуга_Мастер')
        bot.register_next_step_handler(message, add_rasp)

    elif message.text == 'Отменить занятие':
        visitor = name
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
        bot.send_message(message.chat.id, 'Какое услугу хотите отменить?', reply_markup=markup)

    @bot.callback_query_handler(func=lambda callback: 'date_serv:' in callback.data)
    def callback_cancel(callback):
        global name
        date_serv = callback.data.split(':')
        date = date_serv[1]
        service = date_serv[2]
        cursor.execute("SELECT master FROM record WHERE date = ? AND service = ?", (date, napr))
        coach = ''.join(cursor.fetchone())
        cursor.execute("UPDATE record SET visitor = '-' WHERE date = ? AND service = ? AND master = ?",
                       (date, service, master))
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
        button = types.InlineKeyboardButton(napr, callback_data=reg)
        markup.add(button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: 'reg:' in callback.data)
def callback_reg(callback):
    data_parts = callback.data.split(':')
    date = data_parts[1]
    service = data_parts[2]
    cursor.execute("SELECT master FROM record WHERE date = ? AND service = ?", (date, service))
    master = ''.join(cursor.fetchone())
    global name
    update_visitor(date, service, master, name)
    bot.send_message(callback.message.chat.id, f'Вы, {name}, успешно записаны {date} на {service}')

def new_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Ваше имя успешно сохранено.')

def add_rasp(message):
    data = message.text.split('_')[0]
    service = message.text.split('_')[1]
    master = message.text.split('_')[2]
    insert_rasp(data, service, master)
    bot.send_message(message.chat.id, f"В расписание добавилась новая запись:\nДата: {data}\nУслуга: {service}\nМастер: {master}")

bot.polling(none_stop=True) #вызываем команду, благодаря которой бот работает непрерывно.