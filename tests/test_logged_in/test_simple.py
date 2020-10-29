from datetime import datetime, timedelta

import pytest

from netschoolapi import NetSchoolAPI
import os

from netschoolapi.exceptions import WrongCredentialsError
from netschoolapi.utils import take_possible_attachments


@pytest.mark.asyncio
@pytest.fixture
async def nsapi() -> NetSchoolAPI:
    login_data = {
        "login": os.environ["NETSCHOOL_TESTS_LOGIN"],
        "password": os.environ["NETSCHOOL_TESTS_PASSWORD"],
        "school": os.environ["NETSCHOOL_TESTS_SCHOOL"]
    }
    return NetSchoolAPI(os.environ["NETSCHOOL_TESTS_URL"], **login_data)


@pytest.mark.asyncio
async def test_simple_tests(nsapi: NetSchoolAPI):
    async with nsapi as api:
        await api.get_announcements()
        now = datetime(2020, 10, 29)
        diary = await api.get_diary(week_start=now, week_end=now + timedelta(days=60))
        await api.get_lesson_assigns(diary.weekDays[0].lessons[0].assignments[0])
        await api.get_attachments([diary.weekDays[0].lessons[0].assignments[0].id])


@pytest.mark.asyncio
async def test_bad_announcements():
    login_data = {
        "login": "iouoiu123uuoioiuiuo",
        "password": "541232",
        "school": os.environ["NETSCHOOL_TESTS_SCHOOL"]
    }
    # noinspection PyBroadException
    try:
        async with NetSchoolAPI(os.environ["NETSCHOOL_TESTS_URL"], **login_data) as api:
            await api.get_announcements()
    except WrongCredentialsError:
        pass
    else:
        raise Exception()


