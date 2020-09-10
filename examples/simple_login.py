import asyncio

from netschoolapi import NetSchoolAPI


async def main():
    api = NetSchoolAPI("http://sgo.cit73.ru/")
    await api.login("Иван", "Иван555", school="МАОУ многопрофильный лицей №20")
    print(await api.get_announcements())


asyncio.run(main())
