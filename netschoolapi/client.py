import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional

import httpx

from netschoolapi.data import Lesson
from netschoolapi.exceptions import WrongCredentialsError, RateLimitingError, UnknownServerError
from netschoolapi.utils import LoginForm


class NetSchoolAPI:
    at: str = None
    esrn_sec: str = None
    user_id: int = None
    year_id: int = None

    session = httpx.Client()

    def __init__(self, url):
        self.url = url.rstrip("/")

    async def get_form_data(self, for_: Optional[str] = "schools"):
        login_data = LoginForm(url=self.url)
        return list(map(lambda a: a["name"], (await login_data.login_form_data)[for_]))

    async def login(self, login: str, password: str, school: str):
        await self.session.get(self.url)

        resp = await self.session.post(self.url + "/webapi/auth/getdata", data=b'')
        data = resp.json()
        lt, ver, salt = data["lt"], data["ver"], data["salt"]

        login_data = LoginForm(url=self.url)
        await login_data.get_login_data(school=school)

        pw2 = hashlib.new(
            "md5",
            salt.encode() + hashlib.new("md5", password.encode()).hexdigest().encode(),
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
            if "Следующая попытка может быть совершена не ранее чем" in error_message:
                raise RateLimitingError("Rate limited by the server. Try again later.") from err
            elif "Неправильный пароль" in error_message:
                raise WrongCredentialsError("Incorrect credentials provided.") from err
            else:
                raise UnknownServerError("message: " + error_message)
        resp = await self.session.post(
            self.url + "/angular/school/studentdiary/", data={"AT": self.at, "VER": ver}
        )
        self.user_id = (
            int(re.search(r'userId = "(\d+)"', resp.text, re.U).group(1)) - 2
        )  # TODO: Investigate this
        self.year_id = int(re.search(r'yearId = "(\d+)"', resp.text, re.U).group(1))

    async def get_diary(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ):
        if week_start is None:
            week_start = datetime.now() - timedelta(days=7)
        if week_end is None:
            week_end = datetime.now()
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
        return [
            [Lesson().create(lesson_data) for lesson_data in day["lessons"]]
            for day in resp.json()["weekDays"]
        ]
