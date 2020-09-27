import pytest

from netschoolapi import LoginForm


@pytest.fixture
def lf_ulsk():
    return LoginForm("https://sgo.cit73.ru")


@pytest.mark.asyncio
async def test_ulsk_1(lf_ulsk):
    result = await lf_ulsk.get_login_form(
        state="Ульяновская обл",
        province="Чердаклинский район",
        city="Мирный, п.",
        func="Общеобразовательная",
    )

    assert result == {"CID": 2, "SID": 73, "PID": 4, "CN": 132, "SFT": 2, "SCID": 155}


@pytest.mark.asyncio
async def test_ulsk_2(lf_ulsk):
    result = await lf_ulsk.get_login_form(
        state="Ульяновская обл", province="Чердаклинский район", city="Красный Яр, с."
    )

    assert result == {"CID": 2, "SID": 73, "PID": 4, "CN": 490, "SFT": 1, "SCID": 1194}


@pytest.mark.asyncio
async def test_ulsk_3(lf_ulsk):
    result = await lf_ulsk.get_login_form(
        province="Городской округ Новоульяновск",
        func="Общеобразовательная",
        school="МОУ Приволжская ОШ",
    )

    assert result == {"CID": 2, "SID": 73, "PID": -38, "CN": 38, "SFT": 2, "SCID": 389}
