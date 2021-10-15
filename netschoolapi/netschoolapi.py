from datetime import date, timedelta
from hashlib import md5
from io import BytesIO
from typing import Optional, Dict, List, Union

import httpx
from httpx import AsyncClient, Response

from netschoolapi import data, errors, schemas

__all__ = ['NetSchoolAPI']


async def _die_on_bad_status(response: Response):
    response.raise_for_status()


class NetSchoolAPI:
    def __init__(self, url: str):
        url = url.rstrip('/')
        self._client = AsyncClient(
            base_url=f'{url}/webapi',
            headers={'user-agent': 'NetSchoolAPI/5.0.3', 'referer': url},
            event_hooks={'response': [_die_on_bad_status]},
        )

        self._student_id = -1
        self._year_id = -1
        self._school_id = -1

        self._assignment_types: Dict[int, str] = {}
        self._login_data = ()

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def login(self, user_name: str, password: str, school: Union[str, int]):
        response_with_cookies = await self._client.get('logindata')
        self._client.cookies.extract_cookies(response_with_cookies)

        response = await self._client.post('auth/getdata')
        login_meta = response.json()
        salt = login_meta.pop('salt')

        encoded_password = md5(
            password.encode('windows-1251')
        ).hexdigest().encode()
        pw2 = md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]

        try:
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
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.CONFLICT:
                raise errors.AuthError("Incorrect username or password!")
            else:
                raise http_status_error
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

        response = await self._client.get(
            'grade/assignment/types', params={'all': False}
        )
        assignment_reference = response.json()
        self._assignment_types = {
            assignment['id']: assignment['name']
            for assignment in assignment_reference
        }
        self._login_data = (user_name, password, school)

    async def _request_with_optional_relogin(
            self, path: str, method="GET", params: dict = None,
            json: dict = None):
        try:
            response = await self._client.request(
                method, path, params=params, json=json
            )
        except httpx.HTTPStatusError as http_status_error:
            if (
                http_status_error.response.status_code
                == httpx.codes.UNAUTHORIZED
            ):
                if self._login_data:
                    await self.login(*self._login_data)
                    return await self._client.request(
                        method, path, params=params, json=json
                    )
                else:
                    raise errors.AuthError(
                        ".login() before making requests that need "
                        "authorization"
                    )
            else:
                raise http_status_error
        else:
            return response

    async def download_attachment(
            self, attachment: data.Attachment,
            path_or_file: Union[BytesIO, str] = None):
        """
        If `path_to_file` is a string, it should contain absolute path to file
        """
        if path_or_file is None:
            file = open(attachment.name, "wb")
        elif isinstance(path_or_file, str):
            file = open(path_or_file, "wb")
        else:
            file = path_or_file
        file.write((
            await self._request_with_optional_relogin(
                f"attachments/{attachment.id}"
            )
        ).content)

    async def download_attachment_as_bytes(
            self, attachment: data.Attachment) -> BytesIO:
        attachment_contents_buffer = BytesIO()
        await self.download_attachment(
            attachment, path_or_file=attachment_contents_buffer
        )
        return attachment_contents_buffer

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

        response = await self._request_with_optional_relogin(
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
    ) -> List[data.Assignment]:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)

        response = await self._request_with_optional_relogin(
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

    async def announcements(
            self, take: Optional[int] = -1) -> List[data.Announcement]:
        response = await self._request_with_optional_relogin(
            'announcements', params={'take': take}
        )
        announcements = schemas.Announcement().load(response.json(), many=True)
        return [
            data.announcement(announcement)
            for announcement in announcements
        ]

    async def attachments(
            self, assignment: data.Assignment) -> List[data.Attachment]:
        response = await self._request_with_optional_relogin(
            method="POST",
            path='student/diary/get-attachments',
            params={'studentId': self._student_id},
            json={'assignId': [assignment.id]},
        )
        attachments_json = response.json()[0]['attachments']
        attachments = schemas.Attachment().load(attachments_json, many=True)
        return [data.Attachment(**attachment) for attachment in attachments]

    async def school(self):
        response = await self._request_with_optional_relogin(
            'schools/{0}/card'.format(self._school_id)
        )
        school = schemas.School().load(response.json())
        return data.School(**school)

    async def logout(self):
        await self._client.post('auth/logout')
        await self._client.aclose()

    async def _address(self, school: Union[str, int]) -> Dict[str, int]:
        response = await self._client.get(
            'prepareloginform'
        )

        schools_reference = response.json()['schools']
        for school_ in schools_reference:
            if school_['name'] == school or school_['id'] == school:
                self._school_id = school_['id']
                return {
                    'cid': school_['countryId'],
                    'sid': school_['stateId'],
                    'pid': school_['municipalityDistrictId'],
                    'cn': school_['cityId'],
                    'sft': 2,
                    'scid': school_['id'],
                }
        raise errors.SchoolNotFoundError(school)
