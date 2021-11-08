import asyncio
from io import BytesIO

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp.web_request import Request

from bot.handlers import dp, bot
from config import ADMIN_ID, STYLES_PATHS, CONTENTS_PATHS
from net.eval import eval_func


routes = web.RouteTableDef()


@aiohttp_jinja2.template('main.html')
async def get_handler(request: Request):
    return {}


async def get_images_handler(request: Request):
    images_urls = {'contents_urls': CONTENTS_PATHS,
                   'styles_urls': STYLES_PATHS}
    return web.json_response(images_urls)


async def post_handler(request: Request):
    data = await request.post()

    content_img_obj = BytesIO(data['content'].file.read())
    style_img_obj = BytesIO(data['style'].file.read())

    stylized_img_obj = await eval_func(content_img_obj, style_img_obj)

    return web.Response(body=stylized_img_obj.getvalue(), content_type='image/jpeg')


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

    site = web.TCPSite(runner, 'localhost')

    await bot.send_message(ADMIN_ID, "<b>❗ Bot started. /start</b>")

    tasks = [
        site.start(),
        dp.start_polling()
    ]

    print('App started.')
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
