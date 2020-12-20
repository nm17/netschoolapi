from typing import Dict, Tuple

from httpx import AsyncClient

from . import exceptions
from .utils import _json_or_panic


async def _get_login_form(client: AsyncClient,
                          school_address: Tuple[str, str, str, str, str]) -> Dict[str, int]:
    """Получение логин формы школы.

    Arguments:
        client (AsyncClient): см. `client.py/NetSchoolAPI`.
        school_address (Tuple[str, str, str, str, str]): Адрес школы с сайта СГО.

    Returns:
        Dict[str, int]: Логин форма школы.

    Raises:
        NetSchoolAPIError: При неудачном декодировании JSON`а.
        LoginFormError: Если адрес школы указан неправильно.
    """
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
    # И, да, не знаю как можно назвать x по-другому.
    for last_name, x in zip(queue, school_address):
        items = _json_or_panic(await client.get("loginform", params={**login_form, "lastname": last_name}))

        for item in items["items"]:
            if item["name"] == x:
                login_form.update({queue[last_name]: item["id"]})
                break
        else:
            raise exceptions.LoginFormError(queue[last_name], x)

    return login_form
