"""Спасибо @dsolmann."""

import asyncio

from netschoolapi.login_form import get_login_form


async def main():
    login_form = await get_login_form(
        "https://edu.admoblkaluga.ru:444/",
        "Людиновский район",
        "Букань, с.",
        'МКОУ "Букановская средняя школа"',
    )
    assert login_form == {
        "cid": 2,
        "sid": 122,
        "pid": 36,
        "cn": 2025,
        "sft": 2,
        "scid": 149,
    }


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
