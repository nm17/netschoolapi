from netschoolapi.login_form import LoginForm
import asyncio

# Тест нового /webapi/loginform , спасибо dsolmann за то что помог мне разобраться с ним.


async def main():
    url = "https://edu.admoblkaluga.ru:444/"

    lf = LoginForm(url)

    await lf.get_login_form(
        state="Калужская обл",
        province="Людиновский район",
        city="Букань, с.",
        func="Общеобразовательная",
    )

    assert lf.request_params == {
        "CID": 2,
        "SID": 122,
        "PID": 36,
        "CN": 2025,
        "SFT": 2,
        "SCID": 149,
    }
    print(lf.request_params)


asyncio.run(main())
