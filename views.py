import asyncio
import telebot
from aiohttp import web
from bot import Bot

class AioView(web.View):
	async def get(self):
		return web.Response(text="WELCOME")

	async def post(self):
		try:
			jsr = await self.request.json()
			update = telebot.types.Update.de_json(jsr)
			Bot.process_new_updates([update])
		except:
			jsr = "NONE"
		print(jsr)	
		return web.Response(text="")