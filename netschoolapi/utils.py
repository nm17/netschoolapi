from pprint import pprint
from typing import Optional, NamedTuple

import asks
import trio
from loguru import logger


class LoginData:
    CID: int
    SID: int
    PID: int
    CN: int
    SFT: int
    SCID: int
    ECardID = ""

    async def get_login_data(
        self,
        url: str,
        school: str,
        country: Optional[str] = None,
        func: Optional[str] = None,
        province: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
    ):
        # TODO: Reorder everything
        resp = await asks.get(url.rstrip("/") + "/webapi/prepareloginform")
        assert resp.status_code == 200

        data = resp.json()

        logger.debug(data)

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

        logger.debug(
            'School "{school}" found (scid: {scid})', school=school, scid=self.SCID
        )

        logger.debug("Got new login data: {data}", data=self.__dict__)
