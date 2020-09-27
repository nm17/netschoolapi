import pytest

from netschoolapi import LoginForm


@pytest.fixture
def lf_kaluga():
    return LoginForm("https://edu.admoblkaluga.ru:444")


@pytest.mark.asyncio
async def test_kaluga_1(lf_kaluga):
    result = await lf_kaluga.get_login_form(
        state="Калужская обл",
        province="Людиновский район",
        city="Букань, с.",
        func="Общеобразовательная",
    )

    assert result == {
        "CID": 2,
        "SID": 122,
        "PID": 36,
        "CN": 2025,
        "SFT": 2,
        "SCID": 149,
    }


@pytest.mark.asyncio
async def test_kaluga_2_bad(lf_kaluga):
    result = await lf_kaluga.get_login_form(
        state="Калужская обл", province="Людиновский район", city="Букань, с."
    )

    # Проверяем что результат отличается только CN и SCID
    assert set(
        map(
            lambda a: a[0],
            set(result.items()).difference(
                set({"CID": 2, "SID": 122, "PID": 36, "SFT": 2}.items())
            ),
        )
    ) == {"CN", "SCID"}
