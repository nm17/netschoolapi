import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional

import dateutil.parser
import httpx
import dacite

from netschoolapi.data import Announcement
from netschoolapi.exceptions import (
    WrongCredentialsError,
    RateLimitingError,
    UnknownServerError,
)
from netschoolapi.utils import LoginForm


class NetSchoolAPI:
    at: str = None
    esrn_sec: str = None
    user_id: int = None
    year_id: int = None
    logged_in = False

    session = httpx.AsyncClient()

    def __init__(self, url):
        self.url = url.rstrip("/")

    async def get_form_data(self, for_: Optional[str] = "schools"):
        login_data = LoginForm(url=self.url)
        return list(map(lambda a: a["name"], (await login_data.login_form_data)[for_]))

    async def login(
        self,
        login: str,
        password: str,
        school: str,
        city: Optional[str] = None,
        oo: Optional[str] = None,
    ):
        async with self.session:
            await self.session.get(self.url)

            resp = await self.session.post(self.url + "/webapi/auth/getdata", data=b" ")
            data = resp.json()
            lt, ver, salt = data["lt"], data["ver"], data["salt"]

            login_data = LoginForm(url=self.url)
            await login_data.get_login_data(school=school, city=city, func=oo)

            pw2 = hashlib.new(
                "md5",
                salt.encode()
                + hashlib.new("md5", password.encode("windows-1251"))
                .hexdigest()
                .encode(),
            ).hexdigest()
            pw = pw2[: len(password)]

            data = {
                "LoginType": "1",
                **login_data.__dict__,
                "UN": login,
                "PW": pw,
                "lt": lt,
                "pw2": pw2,
                "ver": ver,
            }
            resp = await self.session.post(
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
            resp = await self.session.post(
                self.url + "/angular/school/studentdiary/",
                data={"AT": self.at, "VER": ver},
            )
            self.user_id = (
                int(re.search(r"userId = (\d+)", resp.text, re.U).group(1)) - 2
            )  # TODO: Investigate this
            self.year_id = int(re.search(r'yearId = "(\d+)"', resp.text, re.U).group(1))
            self.logged_in = True

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
            week_start = datetime.now() - timedelta(days=7)
        if week_end is None:
            week_end = datetime.now()
        async with self.session:
            resp = await self.session.get(
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

    async def get_diary_df(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ):
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
        async with self.session:
            return [
                dacite.from_dict(Announcement, a)
                for a in (
                    await self.session.get(f"{self.url}/webapi/announcements?take=-1")
                ).json()
            ]

    async def logout(self):
        """
        Выходит из данной сессии
        """
        async with self.session:
            await self.session.post(
                self.url + "/asp/logout.asp",
                params={"at": self.at, "VER": int(datetime.now().timestamp()) * 100},
                data={},
            )
            # https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/Date/getTime
