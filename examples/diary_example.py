import asyncio
from datetime import datetime, timedelta

from netschoolapi import NetSchoolAPI


async def main():
    login_data = {
        "login": "Иван",
        "password": "Иван228",
        "school": "МАОУ многопрофильный лицей №20"
    }
    async with NetSchoolAPI("http://sgo.cit73.ru/", **login_data) as api:
        diary = await api.get_diary(week_end=datetime.now() + timedelta(days=7))
        for day in diary.weekDays:
            print("Дата:", day.date)
            print("Расписание: ")
            for lession in day.lessons:
                print("\t", lession.subjectName)


asyncio.run(main())