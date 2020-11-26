from datetime import date, timedelta
from hashlib import md5
from typing import Optional, List, Tuple

from httpx import AsyncClient

from . import data
from . import exceptions
from .login_form import _get_login_form
from .utils import _USER_AGENT


class NetSchoolAPI:
    def __init__(self,
                 url: str,
                 user_name: str, password: str,
                 school: Tuple[str, str, str, str, str]):
        """Класс, взаимодействующий с СГО.

        Arguments:
            url (str): Сайт СГО.
            user_name (str): Логин ученика.
            password (str): Пароль для входа.
            school (Tuple[str]): Адрес школы.
        """
        self._client = AsyncClient(
            base_url=f'{url.rstrip("/")}/webapi',
            headers={"user-agent": _USER_AGENT, "Referer": url},
        )
        self._user_name = user_name
        self._password = password

        self._school = school

        self._user_id = None
        self._year_id = None

    async def get_diary(self,
                        week_start: Optional[date] = None,
                        week_end: Optional[date] = None) -> data.Diary:
        """Получить дневник.

        Arguments:
            week_start (Optional[date]): День, с которого начнётся неделя в дневнике.
                                         По умолчанию — понедельник текущей недели.
            week_end (Optional[date]): День, которым закончится неделя в дневнике.
                                       По умолчанию — week_start + 5 дней.

        Returns:
            data.Diary: Дневник.
        """

        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        if not week_end:
            week_end = week_start + timedelta(days=5)

        async with self._client as client:

            response = await client.get(
                "student/diary",
                params={
                    "studentId": self._user_id,
                    "weekStart": week_start.isoformat(),
                    "weekEnd": week_end.isoformat(),
                    "yearId": self._year_id,
                },
            )

            return data.Diary.from_dict(response.json())

    async def get_announcements(self, take: Optional[int] = -1) -> List[data.Announcement]:
        """Получить все объявления.

        Returns:
            List[data.Announcement]: Список объявлений.
        """
        async with self._client as client:
            announcements = (await client.get("announcements", params={"take": take})).json()
            return [data.Announcement.from_dict(a) for a in announcements]

    async def get_details(self, assignment: data.Assignment) -> data.DetailedAssignment:
        async with self._client as client:
            response = await client.get(f"student/diary/assigns/{assignment.id}")
            return data.DetailedAssignment.from_dict(response.json())

    async def get_attachments(self, assignments: List[data.Assignment]) -> List[data.Attachment]:
        async with self._client as client:
            response = await client.post(
                "student/diary/get-attachments",
                params={"studentId": self._user_id},
                json={"assignId": [a.id for a in assignments]},
            )
            return [data.Attachment.from_dict(a) for a in response.json()]

    async def _login(self):
        """Вход в СГО.

        Raises:
            LoginFormError: Если информация о школе указана неверно.
            LoginDataError: При указании неверных логина/пароля.
            NetSchoolAPIError: При прочих ошибках.
        """
        async with self._client as client:
            login_data = (await client.post("auth/getdata")).json()
            salt = login_data.pop("salt")

            encoded_password = md5(self._password.encode("windows-1251")).hexdigest().encode()
            pw2 = md5(salt.encode() + encoded_password).hexdigest()
            pw = pw2[: len(self._password)]

            response = (await client.post(
                "login",
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
                    raise exceptions.LoginDataError
                else:
                    raise exceptions.NetSchoolAPIError(error_message)

            # Access Token
            client.headers["at"] = response["at"]

            diary = (await client.get("student/diary/init")).json()
            student = diary["students"][diary["currentStudentId"]]
            self._user_id = student["studentId"]

            context = (await client.get("context")).json()
            self._year_id = context["schoolYearId"]

    async def _logout(self):
        """Выход из сессии."""
        async with self._client as client:
            await client.post("auth/logout")

    async def __aenter__(self) -> "NetSchoolAPI":
        await self._login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._logout()
