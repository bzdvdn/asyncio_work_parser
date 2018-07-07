import asyncio
from aiohttp import ClientSession

import csv
from bs4 import BeautifulSoup
from random import choice

__author__ = 'bzdvdn'


class Parser(object):
	def __init__(self, url, page, message, chat_id):
		self.message = message
		self.url = url + str(self.message) + "/" 
		self.base_url = self.url 
		self.page = page
		self.chat_id = chat_id


	async def get_fetch(self, client, url, useragent):
		async with client.get(url, headers=useragent) as r:
			return await r.text() 

	async def get_html(self, url, useragent=None):
		async with ClientSession() as client:
			html = await self.get_fetch(client, url, useragent)
			return html


	async def get_total_pages(self, html):
		raise NotImplementedError

	async def write_csv(self, data, message, fileprefix):
		with open(str(self.chat_id) + '_-_' + str(self.message) + '.csv', 'a') as f:
			writer = csv.writer(f)
			writer.writerow((
				data['title'],
				data['company'],
				data['city'],
				data['employment'],
				data['url'],
				data['skills'],
				data['mb_skills'],
			))
			print(data['title'], ' parsed!')

	async def get_pages_data(self, html):
		raise NotImplementedError
	

	async def start_parsing(self, useragent):
		print("-.- -- START parsing -- -.-")
		html = await asyncio.ensure_future(self.get_html(self.url, useragent))
		total_pages = await asyncio.ensure_future(self.get_total_pages(html))	
		tasks = []
		for i in range(1, total_pages+1):
			print("PAGE: {}".format(i))
			url_gen = self.base_url + self.page + str(i)
			html = await asyncio.ensure_future(self.get_html(url_gen, useragent))
			task = asyncio.ensure_future(self.get_pages_data(html))
			tasks.append(task)

		return tasks	

class WorkUaParser(Parser):
	async def get_total_pages(self, html):
		soup = BeautifulSoup(html, "lxml")
		pages = soup.find('ul', class_='pagination' ).find_all('a')[-2].get('href')
		total_pages = int(pages.split('=')[-1])

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
				company = desc_soup.find('dl', class_='dl-horizontal').find('a').find('b').get_text().strip()
				city = desc_soup.find('dl', class_='dl-horizontal').findAll('dd')[-2].get_text().strip()
				employment = desc_soup.find('dl', class_='dl-horizontal').findAll('dd')[-1].get_text().strip()	
			except Exception as e:
				print(e)
			try:
				skills = desc_soup.find('div', class_='wordwrap').find('ul').get_text()
			except:
				skills = ''
			try:
				mb_skills = desc_soup.find('div', class_='wordwrap').find_all('ul')[1].get_text()
			except:
				mb_skills = ''
				


			data = {
					'title': title,
					'company': company,
					'city': city,
					'employment': employment,
					'url': url,
					'skills': skills,
					'mb_skills':mb_skills,
															
			}
			
			await self.write_csv(data=data, message=self.message, fileprefix=str(self.chat_id))

class RabotaUAParser(Parser):
	async def get_total_pages(self, html):
		soup = BeautifulSoup(html, "lxml")
		table = soup.find('div', class_='f-vacancylist-wrap fd-f-left ft-c-stretch').find('div', class_='fd-f1').find('section', class_='f-vacancylist-leftwrap f-paper').find('table', class_='f-vacancylist-tablewrap')
		pages = table.find_all('tr')[-1].find_all('dd')[-2].find('a').get('href')
		total_pages = int(pages.split('=')[-1])
		return int(total_pages)

	async def get_pages_data(self, html):
		soup = BeautifulSoup(html, "lxml")
		ads = soup.find('table', class_='f-vacancylist-tablewrap').find_all('tr')[0:-1]

		for index, iterator in enumerate(ads, start=1):

			try:
				title = iterator.find('td').find('article', class_='f-vacancylist-vacancyblock').find('div',class_='fd-f-left').find('div', class_='fd-f1').find('h3').text.strip()
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
				employment = desc_soup.find('div', class_='d_content').find('div', class_='d_des').find_all('ul')[2].text
			except:
				employment = '----'

			try:
				skills = desc_soup.find('div', class_='d_content').find('div', class_='d_des').find_all('ul')[5].text
			except:
				skills = '----'

			try:
				mb_skills = skills = desc_soup.find('div', class_='d_content').find('div', class_='d_des').find_all('ul')[4].text
			except:
				mb_skills = ''

			data = {
					'title': title,
					'company': company,
					'city': city,
					'employment': employment,
					'skills': skills,
					'mb_skills': mb_skills,
					'url': url	
																
				}

			await self.write_csv(data, str(self.message), str(self.chat_id))


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
				f"Описание: {description}",
				'                   ',
				'-------NEXT-------',
				'                   '
			]

			await self.write_file(data, str(self.message), str(self.chat_id))

	async def write_file(self, data, message, fileprefix):
		with open(str(self.chat_id) + '_-_' + str(self.message) + '.doc', 'a') as f:
			for i in data:
				f.write('\n{}\n'.format(i))

			print(data[0], ' parsed!')


def read_file(filename):
	with open(filename, 'r') as f:
		return f.read().split('\n')

useragent = {'User-Agent': choice(read_file('useragent.txt'))}

def main(useragent):
	# p = WorkUaParser(url='https://www.work.ua/jobs-', page='page=', message='javascript', chat_id='121212121')
	# p = RabotaUAParser(url='https://rabota.ua/jobsearch/vacancy_list?keyWords=', page='&pg=', message='python', chat_id='1111')
	p = HHRUParser(url='https://api.hh.ru/vacancies?text=', page='&page=', message='go', chat_id="222")
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	r = loop.run_until_complete(asyncio.gather(p.start_parsing(useragent)))
	# loop.close()
	
if __name__ == '__main__':
	main(useragent)