import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Union, List

import dacite
import dateutil.parser
import httpx

from .data import (
    Diary,
    Announcement,
    AssignmentInfo,
    LoginFormData,
    Attachment,
    Assignment,
    LessonAttachments,
)
from .exceptions import WrongCredentialsError, RateLimitingError, UnknownServerError
from .login_form import LoginForm
from .utils import get_user_agent, to_dict
from io import BytesIO


def weekday():
    return datetime.today().weekday() + 1


class NetSchoolAPI:
    at: str
    user_id: int
    year_id: int

    def __init__(
        self,
        url: str,
        login: str = None,
        password: str = None,
        login_form: Optional[Union[LoginFormData, dict]] = None,
        school: Optional[str] = None,
        country: Optional[str] = None,
        func: Optional[str] = None,
        province: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        client: httpx.AsyncClient = httpx.AsyncClient(),
    ):
        self.session: httpx.AsyncClient = client
        self.url: str = url.rstrip("/")

        self._login_kwargs = {
            "login": login,
            "password": password,
            "login_form": login_form,
            "school": school,
            "country": country,
            "func": func,
            "province": province,
            "state": state,
            "city": city,
        }

    async def login(
        self,
        login: str,
        password: str,
        login_form: Optional[LoginFormData] = None,
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
                lf = LoginForm(self.url)
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
                **to_dict(login_form),
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

            del self._login_kwargs

    async def get_diary(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ) -> Diary:
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

    async def get_announcements(self) -> List[Announcement]:
        async with self.session as session:
            return [
                dacite.from_dict(Announcement, announcement)
                for announcement in (
                    await session.get(f"{self.url}/webapi/announcements?take=-1")
                ).json()
            ]

    async def get_lesson_assigns(
        self, assignment: Union[Assignment, int]
    ) -> AssignmentInfo:
        """
        Получить доп.инфу о дз
        :param assignment: Либо id дз или сам датакласс Assignment
        :return: Датакласс AssignmentInfo
        """

        if isinstance(assignment, int):
            lesson_id = assignment
        else:
            lesson_id = assignment.id

        async with self.session as session:
            resp = await session.get(
                f"{self.url}/webapi/student/diary/assigns/{lesson_id}?studentId={self.user_id}"
            )

        return dacite.from_dict(AssignmentInfo, resp.json())

    async def get_attachments(self, ids: List[int]) -> List[LessonAttachments]:
        async with self.session as session:
            resp = await session.post(
                self.url
                + f"/webapi/student/diary/get-attachments?studentId={self.user_id}",
                json={"assignId": ids},
            )

        return [
            dacite.from_dict(LessonAttachments, attachments)
            for attachments in resp.json()
        ]

    async def download_file(self, attachment: Attachment) -> BytesIO:
        """
        Скачать файл

        :param attachment: Attachment из diary
        :return: BytesIO
        """
        file = BytesIO()

        async with self.session as session:
            file_url = "{}/webapi/attachments/{}".format(self.url, attachment.id)

            async with session.stream("GET", file_url) as resp:
                async for chunk in resp.aiter_bytes():
                    file.write(chunk)
                    file.flush()
                file.seek(0)

        file.name = attachment.originalFileName
        return file

    async def __aenter__(self):

        if self._login_kwargs["login"] is None:
            raise TypeError("missing required positional argument: 'login'")
        elif self._login_kwargs["password"] is None:
            raise TypeError("missing required positional argument: 'password'")

        await self.login(**self._login_kwargs)
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
