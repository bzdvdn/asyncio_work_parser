import telebot
from flask import Flask
from flask import request
from bot import Bot
import config

app = Flask(__name__)
app.config.from_object(config)

@app.route('/', methods=['POST', 'GET'])
def index():
	if request.method == 'POST':
		r = request.get_json()
		update = telebot.types.Update.de_json(r)
		Bot.process_new_updates([update])
		return ''

	return '<h1> Bot welcomes you</h1>'