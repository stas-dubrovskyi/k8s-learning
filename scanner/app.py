from aiohttp import web


async def health_handler(_request):
    return web.Response(text="alive")


async def scan_handler(request):
    text = (await request.text()).lower()
    for key in ('virus', 'hack'):
        if key in text:
            return web.Response(text="attention")
    return web.Response(text="successful")


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.get('/health', health_handler),
                    web.post('/scan', scan_handler)])
    web.run_app(app)
