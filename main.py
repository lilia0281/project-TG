import telebot
import webbrowser
from telebot import types
import sqlite3
import datetime

bot = telebot.TeleBot('6931176961:AAHA-BQVWqfddpY9JvROJQHbi0Fx6DtYM9A') #токен

#добавление базы данных
conn = sqlite3.connect("beauty_salon.db")
cursor = conn.cursor()

# Создание таблицы для записей
cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL)
""")
conn.commit()

@bot.callback_query_handler(func=lambda callback: True)
def tt(callback):
    if callback.data == 'price':
        file = open('./price.jpeg', 'rb')
        bot.send_photo(callback.message.chat.id, file)

@bot.message_handler(commands=['start']) #декоратор, обрабатываем команду старт
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти на сайт', url='https://supernatural-spn.net/episodes/6-sezon-11-seria/')
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Записаться в салон', callback_data='call')
    btn3 = types.InlineKeyboardButton('Прайс', callback_data='price')
    markup.row(btn2,btn3)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! \nВас приветствует салон красоты Sweety Lemon.', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Записаться в салон')
def appointment(message):
    # Запросить доступные даты и время для записи
    cursor.execute("SELECT date, time FROM appointments")
    appointments = cursor.fetchall()

    available_appointments = []
    for day in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница']:
        for time in ['11:00', '13:00', '15:00', '17:00']:
            if (day, time) not in appointments:
                available_appointments.append((day, time))

    # Отправить сообщение с доступными датами и временем для записи
    message_text = "Свободные даты и время для записи в салон красоты:\n\n"
    for day, time in available_appointments:
        message_text += f"{day} в {time}\n"
    bot.send_message(message.chat.id, message_text)

# Обработчик нажатия на кнопку для выбора даты и времени
@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    data = callback.data.split(',')
    day = data[0]
    time = data[1]


    # Сохранить запись в базе данных
    username = callback.message.chat.username
    cursor.execute("INSERT INTO appointments (username, date, time) VALUES (?, ?, ?)", (username, day, time))
    conn.commit()

    # Отправить подтверждающее сообщение
    bot.answer_callback_query(call.id, text="Вы успешно записаны на {} в {}".format(day, time))


@bot.message_handler()
def main(message):
    if message.text.lower() == ('привет' or 'Привет' or 'Здравствуйте'):
        start(message)

bot.polling(none_stop=True) #вызываем команду, благодаря которой бот работает непрерывно.
