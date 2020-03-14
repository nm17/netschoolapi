from datetime import datetime, timedelta
from re import search
from hashlib import md5

from aiohttp import ClientSession

from webapi import WebApi


class NetSchool:

    _login = "/login"
    _logout = "/asp/logout.asp"

    _diary =  "/diary"

    _referer = "/about.html"

    def __init__(self, url: str) -> None:
        self._url = url.rstrip('/')

    async def login(
            self,
            username: str,
            password: str,
            province: str,
            city: str,
            school: str,
    ) -> None:

        lt, ver, salt = await WebApi.logindata(self._url)

        pw2 = md5(
            salt.encode() +
            md5(password.encode()).hexdigest().encode()
        ).hexdigest()

        PW = pw2[:len(password)]

        login = await WebApi.login(
            self._url,
            {
                **(await WebApi.loginform(
                    self._url,
                    province,
                    city,
                    school
                )),
                "UN": username,
                "PW": PW,
                "pw2": pw2,
                "lt": lt,
                "ver": ver,
            }
        )

        try:
            self._at = login["at"]

        except:
            raise Exception

        async with ClientSession() as session:
            async with session.post(
                self._url,
                data={
                    "at": self._at,
                    "ver": ver,
                }
            ) as response:

                if response.status != 200:
                    raise Exception

                self._userid = int(search(r"userId = \"\d+\"", response.text, response.U).group(1)) - 2
                self._yearid = int(search(r"userId = \"\d+\"", response.text, response.U).group(1))

                self._loggedin = True

    async def logout(self) -> None:
        async with ClientSession() as session:
            await session.post(
                self._url + NetSchool._logout,
                params={
                    "at": self._at,
                    "ver": int(datetime.now().timestamp()) * 100,
                },
            )

