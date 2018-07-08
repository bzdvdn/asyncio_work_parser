import asyncio
from aiohttp import ClientSession

import csv
from bs4 import BeautifulSoup
from random import choice

__author__ = 'bzdvdn'


class Parser(object):
	def __init__(self, url,city, page, message, chat_id):
		self.message = message
		self.url = url
		self.base_url = self.url 
		self.page = page
		self.chat_id = chat_id
		self.city = city

	def get_parsed_url(self, url, city, page, message):
		raise NotImplementedError

	def get_base_url(self, url, city, message):
		raise NotImplementedError


	async def get_fetch(self, client, url, useragent):
		async with client.get(url, headers=useragent) as r:
			return await r.text() 

	async def get_html(self, url, useragent=None):
		async with ClientSession() as client:
			html = await self.get_fetch(client, url, useragent)
			return html


	async def get_total_pages(self, html):
		raise NotImplementedError

	async def write_file(self, data, message, fileprefix):
		with open(str(self.chat_id) + '_-_' + str(self.message) + '.doc', 'a', encoding='utf-8') as f:
			for i in data:
				f.write('\n{}\n'.format(i))

			print("WRITED!")

	async def get_pages_data(self, html):
		raise NotImplementedError
	

	async def start_parsing(self, useragent=None):
		print("-.- -- START parsing -- -.-")
		city = self.city
		url  = self.get_base_url(
				url  	= self.url,
				city 	= city,
				message = self.message,
		)
		print(url)
		html = await asyncio.ensure_future(self.get_html(url, useragent))
		total_pages = await asyncio.ensure_future(self.get_total_pages(html))	
		tasks = []
		if total_pages == 1:
			url_gen = self.get_parsed_url(
				url = self.url,
				city = city, 
				message = self.message,
				page = self.page + str(total_pages)
			)
			print(url_gen)
			html = await asyncio.ensure_future(self.get_html(url_gen, useragent))
			task = await asyncio.ensure_future(self.get_pages_data(html))
			tasks.append(task)
		else:
			for i in range(1, total_pages+1):
				print("PAGE: {}".format(i))
				url_gen = self.get_parsed_url(
					url = self.url,
					city = city, 
					message = self.message,
					page = self.page + str(i)
				)
				print(url_gen)
				html = await asyncio.ensure_future(self.get_html(url_gen, useragent))
				task = asyncio.ensure_future(self.get_pages_data(html))
				tasks.append(task)

		print("-.- -- DONE! -- -.-")

		return tasks	

class WorkUaParser(Parser):
	def get_base_url(self, url, city, message):
		if self.city:
			city = self.city + "-"
		else:
			city = ""
		full_url = url + city + message + "/"

		return full_url
	def get_parsed_url(self, url, city, page, message):
		if self.city:
			city = self.city + "-"
		else:
			city = ""
		full_url = url + city + message + "/" + page

		return full_url

	async def get_total_pages(self, html):
		soup = BeautifulSoup(html, "lxml")
		try:
			pages = soup.find('ul', class_='pagination' ).find_all('a')[-2].get('href')
			total_pages = int(pages.split('=')[-1])
		except:
			total_pages = 1

		return int(total_pages)

	async def get_pages_data(self, html):
		soup = BeautifulSoup(html, "lxml")
		ads = soup.find_all('div', class_='card card-hover card-visited wordwrap job-link')
		for index, iterator in enumerate(ads):
			name  = title = iterator.find('h2').find('a').get('title').strip().lower()
			try:
				title = iterator.find('h2').find('a').get('title').strip().lower()
				url = 'https://www.work.ua' + iterator.find('h2').find('a').get('href')
				print('{} - index, url - {}'.format(index, url))
			except Exception as e:
				print(e)
			try:
				page = await self.get_html(url)
				desc_soup = BeautifulSoup(page, 'lxml')
			except Exception as e:
				print(e)
			try:
				description = desc_soup.find('div', class_='wordwrap').text
			except:
				description = '----'

			data = [
				f"{description}",
				'                   ',
				'-------NEXT-------',
				'                   '
			]
			
			await self.write_file(data=data, message=self.message, fileprefix=str(self.chat_id))

class RabotaUAParser(Parser):
	def get_base_url(self, url, city, message):
		if city:
			full_url = url + "?regionId=" + city + " &keyWords="+ message 
		else:
			full_url = url + "?keyWords=" + message 

		return full_url

	def get_parsed_url(self, url, city, page, message):
		if city:
			full_url = url + "?regionId=" + city + "&keyWords="+ message + page
		else:
			full_url = url + "?keyWords="+ message + page
		print(full_url)

		return full_url

	async def get_total_pages(self, html):
		soup = BeautifulSoup(html, "lxml")

		table = soup.find('div', class_='f-vacancylist-wrap fd-f-left ft-c-stretch').find('div', class_='fd-f1').find('section', class_='f-vacancylist-leftwrap f-paper').find('table', class_='f-vacancylist-tablewrap')
		try:
			pages = table.find_all('tr')[-1].find_all('dd')[-2].find('a').get('href')
			total_pages = int(pages.split('=')[-1])
		except:
		 	total_pages = 1
		return total_pages

	async def get_pages_data(self, html):
		soup = BeautifulSoup(html, "lxml")
		ads = soup.find('table', class_='f-vacancylist-tablewrap').find_all('tr')[0:-1]
		count = soup.find('h2', class_='f-reset-offsets f-merchant').find("span", class_="fd-fat-merchant").text
		
		if int(count) > 0:
			for index, iterator in enumerate(ads, start=1):
				print(self.message)
				try:
					title = iterator.find('td').find('article', class_='f-vacancylist-vacancyblock').find('div',class_='fd-f-left').find('div', class_='fd-f1').find('h3').text.strip()
					print(title)
					company = iterator.find('td').find('article', class_='f-vacancylist-vacancyblock').find('div',class_='fd-f-left').find('div', class_='fd-f1').find('a', class_='f-text-dark-bluegray f-visited-enable').text.strip()
					city = iterator.find('td').find('article', class_='f-vacancylist-vacancyblock').find('div',class_='fd-f-left').find('div', class_='fd-f1').find('div', class_='f-vacancylist-characs-block fd-f-left-middle').find('p', class_='fd-merchant').text.strip()
					url = iterator.find('td').find('article', class_='f-vacancylist-vacancyblock').find('div',class_='fd-f-left').find('div', class_='fd-f1').find('h3').find('a').get('href')
					print('{} - index, url - {}'.format(index,url))

				except Exception as e:
					print("MAIN EXCEPTION")			
				try:
					page = await self.get_html('https://rabota.ua' + url)
					desc_soup = BeautifulSoup(page, "lxml")
				except Exception as e:
					print(e)
				try:
					description = desc_soup.find('div', class_='f-vacancy-description-inner-content').text
				except:
					description = '----'

				data = [
					f'Назвние: {title}',
					f'Город: {city}',
					f'Компания: {company}',
					f'Ссылка: {url}',
					f'Описание: {description}',
					'                   ',
					'-------NEXT-------',
					'                   '
				]

				await self.write_file(data, str(self.message), str(self.chat_id))


class HHRUParser(Parser):
	async def get_fetch(self, client, url, useragent):
		async with client.get(url, headers=useragent) as r:
			return await r.json()

	async def get_total_pages(self, html):
		total_pages = html["pages"]
		return total_pages

	async def get_pages_data(self, html):
		items = html["items"]

		for index, iterator in enumerate(items, start=1):
			name = iterator["name"]
			url = iterator["url"]

			response = await self.get_html(url)
			soup = BeautifulSoup(response["description"], "lxml")

			description = soup.text
			data_url 	= response["alternate_url"]
			city 		= response["area"]["name"]
			company 	= response["employer"]["name"]
			schedule 	= response["schedule"]["name"]
			employment 	= response["employment"]["name"]

			data = [
				f"Название: {name}",
				f"Город: {city}",
				f"Компания: {company}",
				f"Занятось: {schedule},{employment}",
				f"Ссылка: {data_url}",
				f"Описание: {description}",
				'                   ',
				'-------NEXT-------',
				'                   '
			]

			await self.write_file(data, str(self.message), str(self.chat_id))

	


def read_file(filename):
	with open(filename, 'r') as f:
		return f.read().split('\n')

useragent = {'User-Agent': choice(read_file('useragent.txt'))}

def main(useragent):
	# p = WorkUaParser(url='https://www.work.ua/jobs-',city="donetsk", page='?page=', message='php', chat_id='121212121')
	p = RabotaUAParser(url='https://rabota.ua/jobsearch/vacancy_list',city="6", page='&pg=', message='python', chat_id='1111')
	# p = HHRUParser(url='https://api.hh.ru/vacancies?text=', page='&page=', message='go', chat_id="222")
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	r = loop.run_until_complete(asyncio.gather(p.start_parsing(useragent)))
	# loop.close()
	
if __name__ == '__main__':
	main(useragent)