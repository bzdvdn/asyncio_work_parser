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


	async def get_fetch(self, client, url):
		async with client.get(url, skip_auto_headers={"User-Agent": useragent}) as r:
			return await r.text() 

	async def get_html(self, url, useragent=None):
		async with ClientSession() as client:
			html = await self.get_fetch(client, url)
			return html


	async def get_total_pages(self, html):
		soup = BeautifulSoup(html, "lxml")
		pages = soup.find('ul', class_='pagination' ).find_all('a')[-2].get('href')
		total_pages = int(pages.split('=')[-1])

		return int(total_pages)

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

	def get_pages_data(self, html):
		raise NotImplementedError
	

	async def start_parsing(self, useragent):
		print("STARTWORK")
		# url = 'https://www.work.ua/jobs-' + self.message + '/'
		# base_url = 'https://www.work.ua/jobs-' + self.message + '/?'
		# page = 'page='
		html = await asyncio.ensure_future(self.get_html(self.url))
		total_pages = await self.get_total_pages(html)	
		tasks = []
		for i in range(1, total_pages):
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
			
			await self.write_csv(data=data, message=str(self.message), fileprefix=str(self.chat_id))


def read_file(filename):
	with open(filename, 'r') as f:
		return f.read().split('\n')


useragent = {'User-Agent': choice(read_file('useragent.txt'))}

def main(useragent):
	p = WorkUaParser(url='https://www.work.ua/jobs-', page='page=', message='javascript', chat_id='121212121')
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	r = loop.run_until_complete(asyncio.gather(p.start_parsing(useragent)))
	# loop.close()
	
if __name__ == '__main__':
	main(useragent)