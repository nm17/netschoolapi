import asyncio
from client_dev2 import NetSchoolApi


async def main():
    w = NetSchoolApi(url="сайт школы")
    await w.login(
        "логин", "пароль",
        "район",
        "город",
        "школа"
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
