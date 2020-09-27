"""API Сетевого Города."""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, List

import dacite
from dateutil.parser import parse as parse_date
from httpx import AsyncClient

from .data import Announcement
from .exceptions import WrongCredentialsError, RateLimitingError, UnknownServerError
from .login_form import get_login_form
from .utils import get_user_agent


class NetSchoolAPI:
    def __init__(self, url: str):
        """API СГО.

        Argument:
            url: str -- сайт СГО.
        """
        self._client = AsyncClient(base_url=url.rstrip('/'))
        self._client.headers['User-Agent'] = get_user_agent()

        self._at = ''
        self._esrn_sec = ''
        self._user_id = 0
        self._year_id = 0

    async def login(self, login: str, password: str, city: str, province: str, school: str):
        """Выполняет вход в СГО.

        Arguments:
            login: str -- логин, использующийся для входа на сайт.
            password: str -- пароль, использующийся для входа.
            city: str -- город (как на сайте)
            province: str -- .
            school: str -- название школа (как на сайте).

        Raises:
            UnknownLoginData, если адрес школы указан неверно.
            RateLimitingError при слишком частых запросах к СГО.
            WrongCredentialsError, если неверно указан логин или пароль.
            UnknownServerError.
        """
        async with self._client as session:
            await session.get('/')

            response = await session.post('/webapi/auth/getdata', data={})
            json = response.json()
            lt, ver, salt = json['lt'], json['ver'], json['salt']

            login_form = await get_login_form(str(session.base_url), city, province, school)

            encoded_pw = (
                hashlib.md5(password.encode('windows-1251')).hexdigest().encode()
            )
            pw2 = hashlib.md5(salt.encode() + encoded_pw).hexdigest()
            pw = pw2[: len(password)]

            request = {
                'LoginType': 1,
                **login_form,
                'UN': login,
                'PW': pw,
                'lt': lt,
                'pw2': pw2,
                'ver': ver,
            }

            response = await session.post(
                '/webapi/login',
                data=request,
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

            response = await session.post(
                '/angular/school/studentdiary/',
                data={'AT': self._at, 'VER': ver},
            )

            self._user_id = int(
                re.search(r'userId = (\d+)', response.text, re.U).group(1),
            )
            self._year_id = int(
                re.search(r'yearId = "(\d+)"', response.text, re.U).group(1),
            )

    async def get_diary(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ) -> dict:

        if week_start is None:
            week_start = datetime.now() - timedelta(days=datetime.today().weekday() + 1)
        if week_end is None:
            week_end = datetime.now() + timedelta(days=(6 - datetime.today().weekday() + 1))

        diary = await self._client.get(
            '/webapi/student/diary',
            params={
                'studentId': self._user_id,
                'weekEnd': week_end.isoformat(),
                'weekStart': week_start.isoformat(),
                'withLaAssigns': True,
                'yearId': self._year_id,
            },
        )
        return diary.json()

    async def get_diary_df(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ):
        try:
            import pandas as pd
        except ImportError as err:
            raise ModuleNotFoundError(
                'Pandas not installed. Install netschoolapi[tables].'
            ) from err

        response = await self.get_diary(week_start, week_end)
        df = pd.DataFrame()

        for day in response['weekDays']:
            date = parse_date(day['date']).weekday()

            for lesson in day['lessons']:
                try:
                    homework = lesson['assignments'][0]['assignmentName']
                except KeyError:
                    homework = None

                try:
                    mark = lesson['assignments'][0]['mark']['mark']
                except (KeyError, TypeError):
                    mark = None

                subject = lesson['subjectName']

                if lesson['room'] is not None:
                    room = [int(s) for s in lesson['room'].split('/') if s.isdigit()][0]
                else:
                    room = None

                df = df.append(
                    {
                        'Date': date,
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
        announcements = (await self._client.get('/webapi/announcements?take=-1')).json()
        return [dacite.from_dict(Announcement, announcement) for announcement in announcements]

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
