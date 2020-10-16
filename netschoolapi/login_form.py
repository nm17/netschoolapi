"""Модуль для получения loginform'ы."""


from typing import Dict, Optional
from httpx import AsyncClient, StatusCode
from .exceptions import UnknownServerError, UnknownLoginData


async def _get_prepared_login_form(client: AsyncClient) -> Dict[str, int]:
    """Получение id страны, id субъекта и тип ОО.

    Note:
        cid и sid для каждого сайта константны и уникальны, поэтому мы
        можем брать их, не зная информации о конкретной школе.

        sft -- 2 (общеобразовательная), по умолчанию, т.к. подразумевается,
        что пользователь учится в общеобразовательной школе.

    Arguments:
        client: AsyncClient

    Returns:
        dict('cid', 'sid', 'sft')

    Raises:
        UnknownServerError, если запрос неудачный
    """
    response = await client.get('/webapi/prepareloginform')
    if response.status_code != StatusCode.OK:
        raise UnknownServerError(response.json()['message'])
    login_form = response.json()
    return {
        'cid': login_form['cid'],
        'sid': login_form['sid'],
        'sft': 2,
    }


async def get_login_form(
        url: str,
        province: Optional[str] = None,
        city: Optional[str] = None,
        school: Optional[str] = None,
) -> Dict[str, int]:
    """Составление полных данных о местоположении школы.

    Note:
        ВСЁ ПИСАТЬ В ТОЧНОСТИ КАК НА САЙТЕ! ЭТО ВАЖНО!
        Если параметр не указан, будет выбран первый из списка.

        сокращения, которые использует СГО:
            cid (country id) -- номер страны
            sid (state id) -- номер субъекта
            pid (province id) -- номер района
            cn (city number) -- номер населенного пункта
            sft (school function ???) -- тип ОО
            scid (school id) -- номер школы

        алгоритм:
            1. делаем GET-запрос с известными параметрами,
            указывая параметром lastname последний известный.
            2. сравниваем результаты и если нужный нам объект существует,
            сохраняем его.
            3. см. 1.

            В итоге очередь имеет вид:
                передаваемые параметры (lastname)
                cid, sid, sft (sid) ->
                cid, sid, sft, pid (pid) ->
                cid, sid, sft, pid, cn (sft) ! тут указываем sft,
                т.к. нам он уже известен. Если будем указывать cn, то получим
                список типов ОО.
                cid, sid, sft, pid, cn, scid <- то, что получаем в итоге.

    Arguments:
        url: str -- сайт СГО
        province: Optional[str] -- название района
        city: Optional[str] -- название населенного пункта
        school: Optional[str] -- название ОО

    Raises:
        UnknownServerError при неуспешном запросе.
        UnknownLoginData, если какая-то из опций не существует/написана с ошибкой...

    Returns:
        dict('cid', 'sid', 'sft', 'pid', 'cn', 'scid')

    Examples:
        >>> await get_login_form(
        ...     'https://sgo.cit73.ru/',
        ...     'Городской округ Ульяновск',
        ...     'Ульяновск, г.',
        ...     '"Луговская ОШ"',
        ... )
        {'cid': 2,'sid': 73, 'sft': 2, 'pid': -51, 'cn': 51, 'scid': 488}
        >>> await get_login_form('https://dnevnik-kchr.ru/')
        {'cid': 2, 'sid': 9, 'sft': 2, 'pid': -3, 'cn': 3, 'scid': 22}
        >>> await get_login_form(
        ...     'https://edu.admoblkaluga.ru:444/',
        ...     province='Городской округ Обнинск',
        ... )
        {'cid': 2, 'sid': 122, 'sft': 2, 'pid': -4007, 'cn': 4007, 'scid': 550}
    """

    queue = {'sid': 'pid', 'pid': 'cn', 'sft': 'scid'}
    user_form = {'pid': province, 'cn': city, 'scid': school}

    async with AsyncClient(base_url=url) as client:
        login_form = await _get_prepared_login_form(client)

        for last_name in queue.keys():
            response = await client.get(
                '/webapi/loginform', params={**login_form, 'lastname': last_name},
            )
            if response.status_code != StatusCode.OK:
                raise UnknownServerError(response.text)

            items = response.json()['items']

            if user_form[queue[last_name]] is None:
                login_form.update({queue[last_name]: items[0]['id']})
                continue

            for item in items:
                if item['name'] == user_form[queue[last_name]]:
                    login_form.update({queue[last_name]: item['id']})
                    break
            else:
                raise UnknownLoginData(user_form[queue[last_name]])

    return login_form
