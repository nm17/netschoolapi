import asyncio

from netschoolapi import NetSchoolAPI


async def main():
    login_data = {
        "login": "Иван",
        "password": "Иван228",
        "school": "МАОУ многопрофильный лицей №20"
    }
    async with NetSchoolAPI("http://sgo.cit73.ru/", **login_data) as api:
        print(await api.get_announcements())


asyncio.run(main())
