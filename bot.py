import telebot
import os
import asyncio
import config

from parser import WorkUaParser, HHRUParser, RabotaUAParser 

__author__ = 'bzdvdn'

Bot = telebot.TeleBot(config.token)

Bot.remove_webhook()

print(Bot.get_me())

def read_file(filename):
	with open(filename, 'r') as f:
		return f.read().split('\n')

def delete_file(filename):
	os.remove(filename)

@Bot.message_handler(commands=['help'])
def handle_text(message):
	Bot.send_message(message.chat.id, """
		Этот бот парсит сайты(work.ua, rabota.ua, hh.ru):
		на предмет поиска работы и выводит вам сsv файл.
	команды /work_ua, /hh_ru, /rabota_ua
		после нажатия команд нееобходимо выбрать слово из предложенных на клавиатуре:
		по какому критерию вы хотите спарсить сайт. Например Python

		""")


@Bot.message_handler(commands=['start'])
def start_command(message):
	#bot.send_message(message.chat.id, 'начинаем парсить!')
	user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
	user_markup.row('/work_ua','/rabota_ua', '/hh_ru')
	user_markup.row('/help', '/stop')
	Bot.send_message(message.from_user.id, 'Выберите команды для взаимодействия с ботом: ', reply_markup=user_markup)


@Bot.message_handler(commands=["work_ua", "rabota_ua"])
def work_ua_command(message):
	user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
	user_markup.row('Донецк', 'Харьков','Киев',"Днепр")
	user_markup.row('Запорожье', 'Одесса','Полтава',"Львов")
	user_markup.row('Все города')
	user_markup.row('/help', '/stop')
	msg = Bot.send_message(message.from_user.id, 'Выберите город: ', reply_markup=user_markup)
	Bot.register_next_step_handler(msg, city_query, command=message.text)

def city_query(message, command):
	user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
	user_markup.row('python', 'ruby','php')
	user_markup.row('go', 'devops','javascript')
	user_markup.row('1с', 'front-end', 'back-end')
	user_markup.row('системный администратор', 'Программист')
	user_markup.row('/start')
	msg = Bot.send_message(message.from_user.id, 'Выберите критерии для парсинга:', reply_markup=user_markup)
	try:
		if command == '/work_ua':
			city = config.WORK_UA_CITIES.get(message.text)
		elif command == '/rabota_ua':
			city = config.RABOTA_UA_CITIES.get(message.text)
		elif command == '/hh_ru':
			city = config.HHRU_CITIES.get(message.text)
	except KeyError:
		Bot.send_message(message.from_user.id, 'неверный город')
		Bot.send_message(message.from_user.id, 'Нажмите "/start" для повторного взаимодействия с ботом')

	print(city)
	Bot.register_next_step_handler(
		message  = msg, 
		callback = work_parse,
		city 	 = city,
		command  = command
	)


def parse(message, city,parser):

	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	Bot.send_message(message.from_user.id, 'Данные собираються, это может занять некоторое время....')
	
	loop.run_until_complete(parser.start_parsing())
	try:
		file = open(str(message.from_user.id) + '_-_' + str(message.text) + '.doc', 'rb')
		Bot.send_document(message.from_user.id, file)
		delete_file(str(message.from_user.id)  + '_-_' + str(message.text) + '.doc')
		Bot.send_message(message.from_user.id, 'Готово! Для дальнейшей работы нажмите "/start"')
	except:
		Bot.send_message(message.from_user.id, "В этом городе нет вакансий по данному запросу - '{}'".format(message.text))
		Bot.send_message(message.from_user.id, 'Для дальнейшей работы нажмите "/start"')
	

@Bot.message_handler(commands=["hh_ru"])
def hhru_command(message):
	user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
	user_markup.row("Украина", "Россия")
	user_markup.row('Москва', 'Питер','Киев',"Донецк")
	user_markup.row('Одесса', 'Харьков','Запорожье',"Днепр")
	user_markup.row('Нижний Новгород', 'Новосибирск','Ростов-на-Дону')
	user_markup.row('Все города')
	user_markup.row('/help', '/stop')
	msg = Bot.send_message(message.from_user.id, 'Выберите город/страну: ', reply_markup=user_markup)
	Bot.register_next_step_handler(msg, city_query, command=message.text)


def work_parse(message, city,command):
	print(message.text)
	if message.text == '/start':
		start_command(message)
		return None
	if command == '/work_ua':
		parser = WorkUaParser(url='https://www.work.ua/jobs-',city=city, page='?page=', message=message.text, chat_id=message.from_user.id)
	elif command == '/rabota_ua':
		parser = RabotaUAParser(url='https://rabota.ua/jobsearch/vacancy_list',city=city, page='&pg=', message=message.text, chat_id=message.from_user.id)
	elif command == "/hh_ru":
		parser = HHRUParser(url='https://api.hh.ru/vacancies?text=',city=city, page='&page=', message=message.text, chat_id=message.from_user.id)

	parse(message, city, parser)




@Bot.message_handler(commands=['stop'])
def stop_command(message):
	hide_markup = telebot.types.ReplyKeyboardRemove()
	Bot.send_message(message.from_user.id, 'конец взаимодействия с ботом: наберите "/start" для взаимодействия с ботом', reply_markup=hide_markup)
	

Bot.polling(none_stop=True, interval=0)

