import asyncio
import logging
import peewee
import peewee_async
from aiohttp import web, ClientSession
from environs import Env
from jsonformatter import basicConfig


env = Env()
basicConfig(level=env.log_level("LOG_LEVEL", logging.WARNING))
SCANNER_URL = env.str("SCANNER_URL")

# Configure all key-value pairs in a ConfigMap as container environment variables
# https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#configure-all-key-value-pairs-in-a-configmap-as-container-environment-variables
# Secrets as container environment variables
# https://kubernetes.io/docs/concepts/configuration/secret/#use-case-as-container-environment-variables


database = peewee_async.MySQLDatabase(None)


class TestModel(peewee.Model):
    text = peewee.TextField()

    class Meta:
        database = database


async def health_handler(_request):
    return web.Response(text="alive")


async def text_handler(request):
    text = (await request.text()).lower()
    async with request.app['session'].post(SCANNER_URL, data=text.encode()) as resp:
        if await resp.text() == "attention":
            return web.Response(text="not stored", status=403)
    await request.app['objects'].create(TestModel, text=text)
    return web.Response(text="stored")


async def on_startup(app):
    app['session'] = ClientSession()


async def on_shutdown(app):
    await app['session'].close()


if __name__ == "__main__":
    app = web.Application()
    database.init(database=env.str("MYSQL_DATABASE", "test"),
                  user=env.str("MYSQL_USER"),
                  host=env.str("MYSQL_HOST", "mysql"),
                  port=env.int("MYSQL_PORT", 3306),
                  password=env.str("MYSQL_PASSWD"))

    app['objects'] = peewee_async.Manager(database)
    with app['objects'].allow_sync():
        TestModel.create_table(True)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.add_routes([web.get('/health', health_handler),
                    web.post('/text', text_handler)])
    web.run_app(app)
