import asyncio

from netschoolapi import NetSchoolAPI


async def main():

    async with NetSchoolAPI("http://sgo.cit73.ru/") as api:
        await api.login("Иван", "Иван228", school="МАОУ многопрофильный лицей №20")
        print(await api.get_announcements())


asyncio.run(main())
