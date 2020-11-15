from typing import Union, List, Tuple

from httpx import AsyncClient

from . import exceptions


async def _get_prepared_login_form(client: AsyncClient) -> dict:
    async with client:
        response = await client.get("/webapi/prepareloginform")
        if response.status_code != 200:
            exceptions.NetSchoolAPIError(response.json()["message"])
        return response.json()


async def _get_login_form(client: AsyncClient, school: Union[List, Tuple]) -> dict:
    """get_login_form ....

    Returns:
        dict: ...."""
    login_form = {"cid": 2}
    # Решений не измышляю. На данный момент — самое адекватное решение.
    # Кстати, чтобы упростить жизнь в миллионы раз, в API Сетевого дневника
    # нужно изменить одну строку...
    # Ключ — текщий элемент, значение — следующий.
    queue = {"cid": "sid", "sid": "pid", "pid": "cn", "cn": "sft", "sft": "scid"}

    for last_name, x in zip(queue, school):
        response = await client.get("webapi/loginform", params={**login_form, "lastname": last_name})
        for item in response.json()["items"]:
            if item["name"] == x:
                login_form.update({queue[last_name]: item["id"]})
                break
        # Если не нашлось элементов с таким названием
        else:
            raise exceptions.SchoolAddressError(x)

    return login_form
