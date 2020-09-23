import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional

import dacite
import dateutil.parser
import httpx

from .data import Announcement
from .exceptions import (
    WrongCredentialsError,
    RateLimitingError,
    UnknownServerError,
)
from .login_form import LoginForm
from .utils import get_user_agent


class NetSchoolAPI:

    def __init__(self, url):
        self.at: str = None
        self.esrn_sec: str = None
        self.user_id: int = None
        self.year_id: int = None
        self.session = httpx.AsyncClient()
        self.url = url.rstrip("/")

    async def login(
        self,
        login: str,
        password: str,
        *,
        login_form_data: Optional[LoginForm] = None,
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

            if login_form_data is None:
                lf = LoginForm(url=self.url)
                login_form_data = await lf.get_login_form(
                    school=school,
                    city=city,
                    func=func,
                    country=country,
                    state=state,
                    province=province,
                )

            encoded_pw = hashlib.md5(password.encode("windows-1251")).hexdigest().encode()
            pw2 = hashlib.md5(salt.encode() + encoded_pw).hexdigest()
            pw = pw2[: len(password)]

            data = {
                "LoginType": "1",
                **login_form_data,
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
                if "Следующая попытка может быть совершена не ранее чем" in error_message:
                    raise RateLimitingError("Rate limited by the server. Try again later.") from err
                elif "Неправильный пароль" in error_message:
                    raise WrongCredentialsError("Incorrect credentials provided.") from err
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

    async def get_diary(self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None):
        """
        Получает данные дневника с сервера
        :param week_start: начало недели
        :param week_end: конец недели
        :return: Ответ сервера в json
        """
        if week_start is None:
            week_start = datetime.now() - timedelta(days=7)
        if week_end is None:
            week_end = datetime.now()

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

        return resp.json()

    async def get_diary_df(self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None):
        """
        Получает данные дневника с сервера как таблицу pandas
        :param week_start: начало недели
        :param week_end: конец недели
        :return: Ответ сервера как таблица pandas
        """
        try:
            import pandas as pd
        except ImportError as err:
            raise ModuleNotFoundError("Pandas not installed. Install netschoolapi[tables].") from err

        resp = await self.get_diary(week_start, week_end)
        df = pd.DataFrame()

        for day in resp["weekDays"]:
            date = dateutil.parser.parse(day["date"]).weekday()

            for lesson in day["lessons"]:

                try:
                    hw = lesson["assignments"][0]["assignmentName"]
                except KeyError:
                    hw = None

                try:
                    mark = lesson["assignments"][0]["mark"]["mark"]
                    print(mark)
                except (KeyError, TypeError):
                    mark = None

                subject = lesson["subjectName"]
                room = [int(s) for s in lesson["room"].split("/") if s.isdigit()][0]

                df = df.append(
                    {
                        "Date": date,
                        "Homework": hw,
                        "Subject": subject,
                        "Mark": mark,
                        "Room": room,
                    },
                    ignore_index=True,
                )

        df = df.set_index("Date")
        return df

    async def get_announcements(self):
        async with self.session as session:
            return [
                dacite.from_dict(Announcement, announcement)
                for announcement in (await session.get(f"{self.url}/webapi/announcements?take=-1")).json()
            ]

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

