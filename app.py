import asyncio
from io import BytesIO


import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.web_request import Request

from net.eval import eval_func

from config import API_TOKEN, ADMIN_ID, IMAGES_DIR, STYLES_PATHS, CONTENTS_PATHS
from config import bot
from bot.handlers import dp

routes = web.RouteTableDef()


# WEB HANDLERS
@aiohttp_jinja2.template('main.html')
async def get_handler(request: Request):
    return {}


async def get_images_handler(request: Request):
    images_urls = {'contents_urls': CONTENTS_PATHS,
                   'styles_urls': STYLES_PATHS}
    return web.json_response(images_urls)


async def post_handler(request):
    data = await request.post()

    content_img_obj = BytesIO(data['content'].file.read())
    style_img_obj = BytesIO(data['style'].file.read())

    stylized_img_obj = await eval_func(content_img_obj, style_img_obj)

    try:
        await asyncio.sleep(0.5)
        return web.Response(body=stylized_img_obj.getvalue(), content_type='image/jpeg')
    finally:
        stylized_img_obj.close()


async def main():

    app = web.Application(client_max_size=1024 ** 2 * 30)
    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader('templates')
    )

    app.add_routes([web.get(path='/', handler=get_handler),
                    web.get(path='/getimages', handler=get_images_handler),
                    web.post(path='/', handler=post_handler),
                    web.static(prefix='/static', path='static', show_index=True)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "192.168.1.2")
    await bot.send_message(ADMIN_ID, 'Bot started. /start')

    tasks = [
        site.start(),
        dp.start_polling()
    ]
    print('App started.')
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
