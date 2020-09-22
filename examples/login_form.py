from netschoolapi.login_form import LoginForm
import trio

# Тест нового /webapi/loginform , спасибо dsolmann за то что помог мне разобраться с ним.


async def main():
    url = "https://edu.admoblkaluga.ru:444/"

    lf = LoginForm(url)

    result = await lf.get_login_form(
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
    print(result)


trio.run(main)