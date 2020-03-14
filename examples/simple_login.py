import trio

from netschoolapi import NetSchoolAPI


async def main():
    api = NetSchoolAPI("http://sgo.cit73.ru/")
    await api.login("Иван", "Иван555", "МАОУ многопрофильный лицей №20")
    print(await api.get_announcements())

trio.run(main)
