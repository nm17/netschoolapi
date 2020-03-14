from aiohttp import ClientSession

from exceptions import ServerError, WrongCredentialsError


class WebApi:

    _webapi = "/webapi"

    _getdata = "/auth/getdata"
    _prepareloginform = "/prepareloginform"

    _loginform = "/loginform"

    _login = "/login"

    _referer = "/about.html"

    @staticmethod
    async def prepareloginform(url: str) -> dict:
        async with ClientSession() as client:
            async with client.get(
                url + WebApi._webapi + WebApi._prepareloginform
            ) as response:

                if response.status != 200:
                    raise ServerError(
                        response.status,
                        response.reason
                        (await response.json())["message"],
                    )

                data = await response.json()
                return {
                    "cid": data["cid"],
                    "sid": data["sid"],
                    "sft": 2,
                }

    # TODO REFACTOR THIS !!!
    @staticmethod
    async def loginform(
            url: str,
            province,
            city,
            school,
    ) -> dict:

        loginform = await WebApi.prepareloginform(url)
        form = {
            "pid": province,
            "cn": city,
            "scid": school
        }
        lastnames = {
            "sid": "pid",
            "pid": "cn",
            "sft": "scid",
        }

        async with ClientSession() as session:
            for lastname in lastnames:
                async with session.get(
                    url + WebApi._webapi + WebApi._loginform,
                    params={
                        **loginform,
                        "lastname": lastname,
                    }
                ) as response:

                    if response.status != 200:
                        raise ServerError(
                            response.status,
                            response.reason,
                            (await response.json())["message"],
                        )

                    items = (await response.json())["items"]
                    for item in items:
                        if item["name"] == form[lastnames[lastname]]:
                            loginform.update({
                                lastnames[lastname]: item["id"]
                            })
                            break
                    else:
                        raise WrongCredentialsError

        return loginform

    @staticmethod
    async def login(url: str, data: dict) -> None:
        async with ClientSession() as session:
            print(data)
            async with session.post(
                url + WebApi._webapi + WebApi._login,
                data=data,
                headers={"Referer": url + WebApi._referer}
            ) as response:

                if response.status != 200:
                    print(await response.text())
                    raise ServerError(
                        response.status,
                        response.reason,
                        (await response.json())["message"],
                    )

                return await response.json()

    @staticmethod
    async def logindata(url: str) -> tuple:
        async with ClientSession() as session:
            async with session.post(
                url + WebApi._webapi + WebApi._getdata,
                data=b' ',
            ) as response:

                if response.status != 200:
                    raise ServerError(
                        response.status,
                        response.reason,
                        (await response.json())["message"],
                    )

                data = await response.json()
                return data["lt"], data["ver"], data["salt"]
