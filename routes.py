from views import AioView
from aiohttp import web

def setup_routes(app):
	app.add_routes([web.view('/', AioView)])