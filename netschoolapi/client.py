import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Union

import dacite
import dateutil.parser
import httpx

from .data import Diary, Announcement, Lesson, AssignmentsInfo
from .exceptions import WrongCredentialsError, RateLimitingError, UnknownServerError
from .login_form import LoginForm
from .utils import get_user_agent


def weekday():
    return datetime.today().weekday() + 1


class NetSchoolAPI:
    def __init__(self, url):
        self.at: str = None
        self.user_id: int = None
        self.year_id: int = None
        self.session = httpx.AsyncClient()
        self.url = url.rstrip("/")

    async def login(
        self,
        login: str,
        password: str,
        login_form: Optional[LoginForm] = None,
        school: Optional[str] = None,
        country: Optional[str] = None,
        func: Optional[str] = None,
        province: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
    ):
        async with self.session as session:
            await session.get(self.url)

            resp = await session.post(self.url + "/webapi/auth/getdata", data=b" ")
            data = resp.json()
            lt, ver, salt = data["lt"], data["ver"], data["salt"]

            if login_form is None:
                lf = LoginForm(url=self.url)
                login_form = await lf.get_login_form(
                    school=school,
                    city=city,
                    func=func,
                    country=country,
                    state=state,
                    province=province,
                )

            encoded_pw = (
                hashlib.md5(password.encode("windows-1251")).hexdigest().encode()
            )
            pw2 = hashlib.md5(salt.encode() + encoded_pw).hexdigest()
            pw = pw2[: len(password)]

            data = {
                "LoginType": "1",
                **login_form,
                "UN": login,
                "PW": pw,
                "lt": lt,
                "pw2": pw2,
                "ver": ver,
            }

            resp = await session.post(
                self.url + "/webapi/login",
                data=data,
                headers={"Referer": self.url + "/about.html"},  # Referer REQUIRED
            )

            try:
                self.at = resp.json()["at"]

            except KeyError as err:

                error_message = resp.json()["message"]
                # noinspection GrazieInspection
                if (
                    "Следующая попытка может быть совершена не ранее чем"
                    in error_message
                ):
                    raise RateLimitingError(
                        "Rate limited by the server. Try again later."
                    ) from err
                elif "Неправильный пароль" in error_message:
                    raise WrongCredentialsError(
                        "Incorrect credentials provided."
                    ) from err
                else:
                    raise UnknownServerError("message: " + error_message)

            resp = await session.post(
                self.url + "/angular/school/studentdiary/",
                data={"AT": self.at, "VER": ver},
            )

            self.user_id = int(
                re.search(r"userId = (\d+)", resp.text, re.U).group(1)
            )  # Note to self: the -2 thing seems to be fixed.

            self.year_id = int(re.search(r'yearId = "(\d+)"', resp.text, re.U).group(1))
            self.session.headers["User-Agent"] = get_user_agent()
            self.session.headers["at"] = self.at

    async def get_diary(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ):
        """
        Получает данные дневника с сервера
        :param week_start: начало недели
        :param week_end: конец недели
        :return: Ответ сервера в json
        """
        if week_start is None:
            week_start = datetime.now() - timedelta(days=weekday())
        if week_end is None:
            week_end = datetime.now() + timedelta(days=(6 - weekday()))

        async with self.session as s:

            resp = await s.get(
                self.url + "/webapi/student/diary",
                params={
                    "studentId": self.user_id,
                    "weekEnd": week_end.isoformat(),
                    "weekStart": week_start.isoformat(),
                    "withLaAssigns": "true",
                    "yearId": self.year_id,
                },
                headers={"at": self.at},
            )

        return dacite.from_dict(Diary, resp.json())

    async def get_announcements(self):
        async with self.session as session:
            return [
                dacite.from_dict(Announcement, announcement)
                for announcement in (
                    await session.get(f"{self.url}/webapi/announcements?take=-1")
                ).json()
            ]

    async def get_lesson_assigns(self, lesson: Union[Lesson, int]):
        """
        https://netcity.admsakhalin.ru:11111/webapi/student/diary/assigns/344437549?studentId=133064643
        """

        if isinstance(lesson, int):
            lesson_id = lesson
        else:
            lesson_id = lesson.assignments[0].id

        async with self.session as session:
            resp = await session.get(f"{self.url}/webapi/student/diary/assigns/{lesson_id}?studentId={self.user_id}")

        return dacite.from_dict(AssignmentsInfo, resp.json())

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def logout(self):
        """
        Выходит из данной сессии
        """
        async with self.session as session:
            await session.post(
                self.url + "/asp/logout.asp",
                params={"at": self.at, "VER": int(datetime.now().timestamp()) * 100},
                data={},
            )
