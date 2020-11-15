from datetime import date, timedelta
from hashlib import md5
from re import search, U
from typing import Optional, Union, List, Tuple

from httpx import AsyncClient

from . import data
from . import exceptions
from .login_form import _get_login_form
from .utils import _USER_AGENT


class NetSchoolAPI:
    """Основной класс netschoolapi."""

    def __init__(self, url: str, user_name: str, password: str, school: Union[List, Tuple]):
        """nope.

        Arguments:
            url (str): Сайт СГО.
            user_name (str): ....
            password (str): ....
        """
        self._client = AsyncClient(
            base_url=url.rstrip("/"),
            headers={"user-agent": _USER_AGENT, "Referer": url},
        )
        self._user_name = user_name
        self._password = password

        if len(school) == 0:
            raise
        self._school = school

        self._user_id = None
        self._year_id = None

        self._access_token = None

    async def get_diary(
        self,
        week_start: Optional[date] = date.today(),
        week_end: Optional[date] = date.today() + timedelta(days=6)
    ) -> data.Diary:
        async with self._client as client:

            response = await client.get(
                "/webapi/student/diary",
                params={
                    "studentId": self._user_id,
                    "weekStart": week_start.isoformat(),
                    "weekEnd": week_end.isoformat(),
                    "yearId": self._year_id,
                },
            )

            return data.Diary.from_dict(response.json())

    async def get_announcements(self) -> List[data.Announcement]:
        async with self._client as client:
            announcements = (await client.post("/webapi/announcements?take=-1")).json()
            return [data.Announcement.from_dict(a) for a in announcements]

    async def _login(self):
        async with self._client as client:
            login_data = (await client.post("webapi/auth/getdata")).json()
            salt = login_data.pop("salt")

            encoded_password = md5(self._password.encode("windows-1251")).hexdigest().encode()
            pw2 = md5(salt.encode() + encoded_password).hexdigest()
            pw = pw2[: len(self._password)]

            response = (await client.post(
                "/webapi/login",
                data={
                    "logintype": 1,
                    **(await _get_login_form(client, self._school)),
                    "un": self._user_name,
                    "pw": pw,
                    "pw2": pw2,
                    **login_data,
                },
            )).json()

            if "at" not in response:
                error_message = response["message"]
                if len(error_message) == 29:
                    raise exceptions.WrongIdentityError

            self._access_token = response["at"]
            client.headers["at"] = self._access_token

            diary = (await client.get("webapi/student/diary/init")).json()
            student = diary["students"][diary["currentStudentId"]]
            self._user_id = student["studentId"]

            # К сожалению, мы не можем получить year_id более лёгким способом.
            # Возможно, никогда не сможем, т.к. это значение нельзя получить
            # через API. По крайней мере мы пока не нашли способ.
            response = (await client.post(
                "/angular/school/studentdiary/",
                data={"at": self._access_token, "ver": login_data["ver"]},
            )).text
            self._year_id = int(search(r'yearId = "(\d+)"', response, U).group(1))

    async def _logout(self):
        async with self._client as client:
            await client.post("/asp/logout.asp")

    async def __aenter__(self) -> "NetSchoolAPI":
        self._login_form = await _get_login_form(self._client, self._school)
        await self._login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._logout()
