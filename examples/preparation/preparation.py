import asyncio
from typing import Callable, Awaitable

# noinspection PyUnresolvedReferences
# because working path from an IDE project not always equals to a working path
# when launching the script (so if I launch something from examples, my working
# directory will be "examples", but my IDE thinks that it is "examples/.."
# (project root))
from config.config_maker import Config, make_config

import netschoolapi


async def login(config: Config) -> netschoolapi.NetSchoolAPI:
    client = netschoolapi.NetSchoolAPI(config.url)
    await client.login(config.user_name, config.password, config.school)
    return client


async def _run_main(main):
    config = make_config()
    client = await login(config)
    async with client:
        await main(client)


def run_main(main: Callable[[netschoolapi.NetSchoolAPI], Awaitable]):
    asyncio.get_event_loop().run_until_complete(_run_main(main))
