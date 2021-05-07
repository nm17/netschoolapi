from datetime import date, timedelta
from hashlib import md5
from typing import Optional

from httpx import AsyncClient, Response

from netschoolapi import data, errors, schemas


__all__ = ['NetSchoolAPI']


async def _die_on_bad_status(response: Response):
    response.raise_for_status()


class NetSchoolAPI:
    def __init__(self, url: str):
        url = url.rstrip('/')
        self._client = AsyncClient(
            base_url='{0}/webapi'.format(url),
            headers={'user-agent': 'NetSchoolAPI/5.0.0', 'referer': url},
            event_hooks={'response': [_die_on_bad_status]},
        )

        self._student_id = -1
        self._year_id = -1

        self._assignment_types = dict[int, str]()

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def login(self, user_name: str, password: str, school: str):
        response_with_cookies = await self._client.get('logindata')
        self._client.cookies.extract_cookies(response_with_cookies)

        response = await self._client.post('auth/getdata')
        login_meta = response.json()
        salt = login_meta.pop('salt')

        encoded_password = md5(password.encode('windows-1251')).hexdigest().encode()
        pw2 = md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]

        response = await self._client.post(
            'login',
            data={
                'loginType': 1,
                **(await self._address(school)),
                'un': user_name,
                'pw': pw,
                'pw2': pw2,
                **login_meta,
            },
        )
        auth_result = response.json()

        if 'at' not in auth_result:
            raise errors.AuthError(auth_result['message'])

        self._client.headers['at'] = auth_result['at']

        response = await self._client.get('student/diary/init')
        diary_info = response.json()
        student = diary_info['students'][diary_info['currentStudentId']]
        self._student_id = student['studentId']

        response = await self._client.get('years/current')
        year_reference = response.json()
        self._year_id = year_reference['id']

        response = await self._client.get('grade/assignment/types', params={'all': False})
        assignment_reference = response.json()
        self._assignment_types = {
            assignment['id']: assignment['name'] for assignment in assignment_reference
        }

    async def diary(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> data.Diary:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._client.get(
            'student/diary',
            params={
                'studentId': self._student_id,
                'yearId': self._year_id,
                'weekStart': start.isoformat(),
                'weekEnd': end.isoformat(),
            },
        )
        diary_schema = schemas.Diary()
        diary_schema.context['assignment_types'] = self._assignment_types
        return data.diary(diary_schema.load(response.json()))

    async def overdue(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> list[data.Assignment]:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._client.get(
            'student/diary/pastMandatory',
            params={
                'studentId': self._student_id,
                'yearId': self._year_id,
                'weekStart': start.isoformat(),
                'weekEnd': end.isoformat(),
            },
        )
        assignments = schemas.Assignment().load(response.json(), many=True)
        return [data.Assignment(**assignment) for assignment in assignments]

    async def announcements(self, take: Optional[int] = -1) -> list[data.Announcement]:
        response = await self._client.get('announcements', params={'take': take})
        announcements = schemas.Announcement().load(response.json(), many=True)
        return [data.Announcement(**announcement) for announcement in announcements]

    async def attachments(self, assignment: data.Assignment) -> list[data.Attachment]:
        response = await self._client.post(
            'student/diary/get-attachments',
            params={'studentId': self._student_id},
            json={'assignId': [assignment.id]},
        )
        attachments_json = response.json()[0]['attachments']
        attachments = schemas.Attachment().load(attachments_json, many=True)
        return [data.Attachment(**attachment) for attachment in attachments]

    async def logout(self):
        await self._client.post('auth/logout')
        await self._client.aclose()

    async def _address(self, school: str) -> dict[str, int]:
        response = await self._client.get('addresses/schools', params={'funcType': 2})

        schools_reference = response.json()
        for school_ in schools_reference:
            if school_['name'] == school:
                return {
                    'cid': school_['countryId'],
                    'sid': school_['stateId'],
                    'pid': school_['municipalityDistrictId'],
                    'cn': school_['cityId'],
                    'sft': 2,
                    'scid': school_['id'],
                }
        raise errors.SchoolNotFoundError(school)
