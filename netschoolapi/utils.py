from typing import Optional

import httpx


class LoginForm:
    CID: int
    SID: int
    PID: int
    CN: int
    SFT: int
    SCID: int
    ECardID = ""

    def __init__(self, url):
        self.__url = url

    @property
    async def login_form_data(self) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.__url.rstrip("/") + "/webapi/prepareloginform")
            assert resp.status_code == 200

            return resp.json()

    async def get_login_data(
        self,
        school: str,
        country: Optional[str] = None,
        func: Optional[str] = None,
        province: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
    ):
        # TODO: Reorder everything
        data = await self.login_form_data

        countries = {item["name"].strip(): item["id"] for item in data["countries"]}
        cities = {item["name"].strip(): item["id"] for item in data["cities"]}
        funcs = {item["name"].strip(): item["id"] for item in data["funcs"]}
        provinces = {item["name"].strip(): item["id"] for item in data["provinces"]}
        schools = {item["name"].strip(): item["id"] for item in data["schools"]}

        states = {item["name"].strip(): item["id"] for item in data["states"]}

        self.CID = data["cid"] if country is None else countries[country]
        self.CN = data["cn"] if city is None else cities[city]
        self.PID = data["pid"] if province is None else provinces[province]
        self.SFT = data["sft"] if func is None else funcs[func]
        self.SID = data["sid"] if state is None else states[state]
        self.SCID = data["scid"] if school is None else schools[school]
