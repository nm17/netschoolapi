"""API Сетевого Города."""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, List

import dacite
from httpx import AsyncClient

from .data import Announcement, Diary
from .exceptions import WrongCredentialsError, RateLimitingError, UnknownServerError
from .login_form import get_login_form
from .utils import _get_user_agent


class NetSchoolAPI:
    def __init__(self, url: str):
        """API СГО.

        Argument:
            url: str -- сайт СГО.
        """
        self._client = AsyncClient(base_url=url.rstrip('/'))
        self._client.headers['User-Agent'] = _get_user_agent()

        self._at = ''
        self._esrn_sec = ''
        self._user_id = 0
        self._year_id = 0

    async def login(self, login: str, password: str, province: str, city: str, school: str):
        """Выполняет вход в СГО.

        Arguments:
            login: str -- логин, использующийся для входа на сайт.
            password: str -- пароль, использующийся для входа.
            province: str -- округ/район.
            city: str -- город (как на сайте)
            school: str -- название школа (как на сайте).

        Raises:
            UnknownLoginData, если адрес школы указан неверно.
            RateLimitingError при слишком частых запросах к СГО.
            WrongCredentialsError, если неверно указан логин или пароль.
            UnknownServerError.
        """
        async with self._client as session:
            login_data = (await session.post('/webapi/auth/getdata', data={})).json()
            lt, ver, salt = login_data['lt'], login_data['ver'], login_data['salt']

            encoded_password = (
                hashlib.md5(password.encode('windows-1251')).hexdigest().encode()
            )
            pw2 = hashlib.md5(salt.encode() + encoded_password).hexdigest()
            pw = pw2[: len(password)]

            login_form = await get_login_form(str(session.base_url), province, city, school)

            request_parameters = {
                'LoginType': 1,  # забавный факт -- LoginType может иметь значения от 0 до 8,
                                 # но не 7. почему? никто не знает...
                **login_form,
                'UN': login,
                'PW': pw,
                'lt': lt,
                'pw2': pw2,
                'ver': ver,
            }

            response = await session.post(
                '/webapi/login',
                data=request_parameters,
                headers={'Referer': f'{session.base_url}/about.html'},
            )

            try:
                at = response.json()['at']
                self._at = self._client.headers['at'] = at

            except KeyError as error:
                error_message = response.json()['message']
                if 'Следующая попытка может' in error_message:
                    raise RateLimitingError(error_message) from error
                if 'Неправильный пароль' in error_message:
                    raise WrongCredentialsError(error_message) from error
                raise UnknownServerError(error_message) from error

            student = (await session.get('webapi/student/diary/init')).json()['students'][0]
            self._user_id = student['studentId']

            diary_page = await session.post('/angular/school/studentdiary/', data={'AT': self._at})
            self._year_id = int(
                re.search(r'yearId = "(\d+)"', diary_page.text, re.U).group(1),
            )

    async def get_diary(
        self,
        week_start: Optional[datetime] = datetime.today(),
        week_end: Optional[datetime] = datetime.today() + timedelta(days=6),
    ) -> Diary:

        diary = (await self._client.get(
            '/webapi/student/diary',
            params={
                'studentId': self._user_id,
                'weekStart': week_start.date().isoformat(),
                'weekEnd': week_end.date().isoformat(),
                'yearId': self._year_id,
            },
        )).json()

        return Diary.from_dict(diary)

    async def get_diary_df(
        self,
        week_start: Optional[datetime] = datetime.today(),
        week_end: Optional[datetime] = datetime.today() + timedelta(days=6),
    ):
        try:
            import pandas as pd
        except ImportError as err:
            raise ModuleNotFoundError(
                'Pandas not installed. Install netschoolapi[tables].'
            ) from err

        diary = await self.get_diary(week_start, week_end)
        df = pd.DataFrame()

        for day in diary.weekDays:
            for lesson in day.lessons:
                subject = lesson.subject
                room = lesson.room
                homework = lesson.homework()
                mark = lesson.mark()

                df = df.append(
                    {
                        'Date': day.date,
                        'Homework': homework,
                        'Subject': subject,
                        'Mark': mark,
                        'Room': room,
                    },
                    ignore_index=True,
                )

        df = df.set_index('Date')
        return df

    async def get_announcements(self) -> List[Announcement]:
        """Получение объявлений.

         Returns:
             list[Announcement] -- объявления.
         """
        announcements = (await self._client.get('/webapi/announcements?take=-1')).json()
        return [Announcement.from_dict(announcement) for announcement in announcements]

    async def logout(self):
        """Выход из сессии."""
        await self._client.post(
            '/asp/logout.asp',
            params={'at': self._at, 'VER': int(datetime.now().timestamp()) * 100},
        )
        await self._client.aclose()

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()
