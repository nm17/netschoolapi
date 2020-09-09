from dataclasses import dataclass
from typing import Optional

import httpx
import random

ALL_LOGIN_KWARGS = ["country", "state", "province", "city", "func", "school"]
LOGIN_FORM_QUEUE = {
    "countries": "CID",
    "states": "SID",
    "provinces": "PID",
    "cities": "CN",
    "funcs": "SFT",
    "schools": "SCID",
}


class LoginForm:
    SID: int
    PID: int
    CN: int
    SFT: int
    CID: int
    SCID: int
    ECardID = ""  # TODO: Remove in later versions?

    def __init__(self, url: Optional[str] = None):
        self.__url = url
        self.__client = None

    async def get_prepare_form_data(self) -> dict:
        self.__client = self.__client or httpx.AsyncClient()
        async with self.__client as client:
            resp = await client.get(self.__url.rstrip("/") + "/webapi/prepareloginform")
            assert resp.status_code == 200

            return resp.json()

    async def get_login_data(self, **request_params):
        self.__client = self.__client or httpx.AsyncClient()

        items = list(LOGIN_FORM_QUEUE.values())
        last_name = items[
            max(map(lambda a: items.index(a.upper()), request_params.keys()))
        ].lower()
        request_params["cacheVer"] = random.randint(1000000, 100000000)
        request_params["LASTNAME"] = last_name
        self.__client = self.__client or httpx.AsyncClient()
        async with self.__client as client:
            resp = await client.get(
                self.__url.rstrip("/") + "/webapi/loginform", params=request_params
            )

            return last_name, resp.json()["items"]

    # noinspection PyTypeChecker
    @property
    def request_params(self):
        return dict(filter(lambda a: not a[0].startswith("_"), self.__dict__.items()))

    async def get_login_form(self, **login_kwargs):
        # TODO: Reorder everything and make it not look ugly without pulling in
        # TODO: other libs

        prepare_data = await self.get_prepare_form_data()

        item_reordered = {
            item["name"].strip(): item["id"]
            for item in prepare_data[list(LOGIN_FORM_QUEUE.keys())[0]]
        }

        first_name = list(LOGIN_FORM_QUEUE.values())[0]

        setattr(
            self,
            first_name,  # class attribute name
            prepare_data[first_name.lower()]  # default
            if login_kwargs.get(ALL_LOGIN_KWARGS[0], None)
            is None  # use default if param is none
            else item_reordered[login_kwargs[ALL_LOGIN_KWARGS[0]]],
        )

        for login_arg in ALL_LOGIN_KWARGS[1:]:
            last_name, items = await self.get_login_data(**self.request_params)

            items = {item["name"].strip(): item["id"] for item in items}

            next_name = list(LOGIN_FORM_QUEUE.values())[
                list(LOGIN_FORM_QUEUE.values()).index(last_name.upper()) + 1
            ]

            setattr(
                self,
                next_name,  # class attribute name
                list(items.values())[0]  # default
                if login_kwargs.get(login_arg, None)
                is None  # use default if param is none
                else items[login_kwargs[login_arg]],
            )
