# -*- coding: utf-8 -*-

"""Пример использования netschoolapi."""

import asyncio

from netschoolapi import netscholapi as nsa


async def example():
    """Пример входа.

    Что здесь показано:
        1. вход в СГО.
        2...

    TODO`s:
        1. дописать нужное.
        2. добавить примеров.
    """
    student = await nsa.login(
        url='адрес СГО вашей школы',
        username='логин',
        password='пароль',
        address=(
            'район',
            'населенный пункт',
            'школа',
        ),
    )

    # print(await student.announcements())
    # await student.logout()


loop = asyncio.get_event_loop()
loop.run_until_complete(example())
