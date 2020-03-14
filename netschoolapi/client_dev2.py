import re
from hashlib import md5
from aiohttp import ClientSession

from webapi import WebApi
from exceptions import UnknownError


class NetSchoolApi:

    _login = "/login"
    _diary = "/angular/student/diary"

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
            salt.encode()
            + md5(password.encode("windows-1251")).hexdigest().encode()
        ).hexdigest()
        pw = pw2[:len(password)]

        print(pw, pw2)

        # TODO make this fucking pretty!
        response = await WebApi.login(
            self._url,
            {
                "LoginType": "1",
                **(await WebApi.loginform(
                    self._url,
                    province,
                    city,
                    school,
                )),
                "UN": username,
                "PW": pw,
                "lt": lt,
                "pw2": pw2,
                "ver": ver,
            }
        )

        try:
            at = response["at"]

        except KeyError as error:
            errormessage = response["message"]

            # TODO сделать нормальную обработку
            raise UnknownError(errormessage)

        async with ClientSession() as session:
            async with session.post(
                self._url + NetSchoolApi._diary,
                data={
                    "AT": at,
                    "VER": ver,
                }
            ) as response:
                self.user_id = (
                        int(re.search(r'userId = "\d+"', resp.text, re.U).group(1)) - 2
                )  # TODO: Investigate this
                self.year_id = int(re.search(r'yearId = "\d+"', resp.text, re.U).group(1))
                self.logged_in = True
