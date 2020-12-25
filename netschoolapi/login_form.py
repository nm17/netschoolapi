from typing import Dict, Tuple

from httpx import AsyncClient

from netschoolapi import exceptions
from netschoolapi.utils import _json_or_panic


async def _get_login_form(
    client: AsyncClient,
    school_address: Tuple[str, str, str, str, str],
) -> Dict[str, int]:
    country_id = _json_or_panic(await client.get("/prepareloginform"))["cid"]
    login_form = {"cid": country_id}

    # Решений не измышляю. На данный момент — самое адекватное.
    # Кстати, чтобы упростить жизнь в миллионы раз, в API Сетевого дневника
    # нужно изменить одну строку.
    # Ключ — текущий элемент, значение — следующий.
    queue = {"cid": "sid", "sid": "pid", "pid": "cn", "cn": "sft", "sft": "scid"}

    # Для x должно быть подходящее название, но нет.
    # Это те самые значения с главной странички:
    #   - Регион
    #   - Округ/район
    #   - и т.д.
    # Может, unit тоже не очень?
    for last_name, address_unit in zip(queue, school_address):
        lf = _json_or_panic(await client.get("loginform", params={**login_form, "lastname": last_name}))
        possible_units = lf["items"]

        for unit in possible_units:
            if unit["name"] == address_unit:
                login_form.update({queue[last_name]: unit["id"]})
                break
        else:
            raise exceptions.LoginFormError(queue[last_name], address_unit)

    return login_form
