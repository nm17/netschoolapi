# -*- coding: utf-8 -*-

"""API Сетевого Города."""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, List

import dacite
import dateutil.parser
import httpx

from .data import Announcement
from .exceptions import (
    WrongCredentialsError,
    RateLimitingError,
    UnknownServerError,
)
from .login_form import get_login_form
from .utils import get_user_agent


class NetSchoolAPI:
    def __init__(self, url: str):
        self.__session = httpx.AsyncClient()
        self.__session.headers['User-Agent'] = get_user_agent()

        self.__at = ''
        self.__esrn_sec = ''
        self.__user_id = 0
        self.__year_id = 0

        assert isinstance(url, str), 'Аргумент `url` должен иметь тип `str`'
        self.url = url.rstrip('/')

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
        """
        async with self.__session as session:
            await session.get(self.url)

            response = await session.post(f'{self.url}/webapi/auth/getdata', data=b' ')
            json = response.json()
            lt, ver, salt = json['lt'], json['ver'], json['salt']

            login_form = await get_login_form(session, self.url, city, province, school)

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
                f'{self.url}/webapi/login',
                data=request,
                headers={'Referer': f'{self.url}/about.html'},
            )

            try:
                self.__at, self.__session.headers['at'] = response.json()['at']

            except KeyError as error:
                error_message = response.json()['message']
                if 'Следующая попытка может' in error_message:
                    raise RateLimitingError(error_message) from error
                if 'Неправильный пароль' in error_message:
                    raise WrongCredentialsError(error_message) from error
                raise UnknownServerError(error_message) from error

            response = await session.post(
                f'{self.url}/angular/school/studentdiary/',
                data={'AT': self.__at, 'VER': ver},
            )

            self.__user_id = int(
                re.search(r'userId = (\d+)', response.text, re.U).group(1)
            )
            self.__year_id = int(
                re.search(r'yearId = "(\d+)"', response.text, re.U).group(1)
            )

    async def get_diary(
        self, week_start: Optional[datetime] = None, week_end: Optional[datetime] = None
    ) -> dict:

        if week_start is None:
            week_start = datetime.now() - timedelta(days=datetime.today().weekday() + 1)
        if week_end is None:
            week_end = datetime.now() + timedelta(days=(6 - datetime.today().weekday() + 1))

        diary = await self.__session.get(
            f'{self.url}/webapi/student/diary',
            params={
                'studentId': self.__user_id,
                'weekEnd': week_end.isoformat(),
                'weekStart': week_start.isoformat(),
                'withLaAssigns': True,
                'yearId': self.__year_id,
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
            date = dateutil.parser.parse(day['date']).weekday()

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
        announcements = (await self.__session.get(f'{self.url}/webapi/announcements?take=-1')).json()
        return [dacite.from_dict(Announcement, announcement) for announcement in announcements]

    async def logout(self):
        await self.__session.post(
            f'{self.url}/asp/logout.asp',
            params={'at': self.__at, 'VER': int(datetime.now().timestamp()) * 100},
        )

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()
