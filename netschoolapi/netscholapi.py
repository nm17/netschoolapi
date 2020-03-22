# -*- coding: utf-8 -*-

"""Модуль, использующийся для получения loginform и входа в СГО."""

from hashlib import md5

from re import search
from re import U as unicode

from aiohttp import ClientSession

from data.student import Student
from utilities.handler import handle
from utilities import routes

from utilities.exceptions import LoginformError


async def login(
        url: str,
        username: str,
        password: str,
        address: tuple,
) -> Student:
    """Выполняет вход в СГО.

    Arguments:
        url (str) : адрес СГО, который использует школа.
        username (str) : логин, использующийся на сайте.
        password (str) : пароль, использующийся для входа.
        address (tuple) : адрес школы в виде (район, населенный пункт, школа)

    Returns:
        (Student) : класс, непосредственно взаимодействующий с СГО.
    """
    loginform = await _loginform(url, *address)

    async with ClientSession() as session:

        # временные параметры, используемые для входа
        lt, ver, salt = (await handle(await session.post(
            url=routes.WEBAPI.format(url, routes.GETDATA),
            data={},
        ))).values()

        # зашифрованный пароль
        pw2 = md5(
            salt.encode() +
            md5(password.encode('windows-1251')).hexdigest().encode(),
        ).hexdigest()

        # зашифрованный пароль, обрезанный по длине пароля
        pw = pw2[:len(password)]

        # заготовка для занесения в бд. в будщем
        # TODO шифровать пароли и вообще сделать с этим что-то
        # userdata = {
        #     'username': username,
        #     'password': password,
        #     'loginform': loginform,
        # }

        logindata = {
            'logintype': 1,
            'un': username,
            'pw2': pw2,
            'pw': pw,
            **loginform,
            'lt': lt,
            'ver': ver,
        }

        response = await handle(await session.post(
            url=routes.WEBAPI.format(url, routes.LOGIN),
            data=logindata,
            headers={'referer': routes.REFERER.format(url)},
        ))

        # пока что не обрабатываем ошибки
        at = response['at']

        response = await session.post(
            url='{0}/angular/school/studendiary/',
            params={'at': at, 'ver': ver},
        )

        text = await response.text()
        return Student(
            # TODO как-то получше можно искать?
            uid=int(search(r'userId = (\d+)', text, unicode).group(1)) - 2,
            yid=int(search(r'yearId = (\d+)', text, unicode).group(1)),
            at=at,
        )


async def _loginform(
        url: str,
        province: str,
        city: str,
        school: str,
) -> dict:
    """Составление полных данных о местоположении школы.

    Note:
        ВСЁ ПИСАТЬ В ТОЧНОСТИ КАК НА САЙТЕ! ЭТО ВАЖНО!

        сокращения, которые использует СГО:
            cid (country id) : номер страны.
            sid (state id) : номер субъекта.
            pid (province id) : номер района.
            cn (city number) : номер населенного пункта.
            sft (school function ???) : тип ОО.
            scid (school id) : номер школы.

        алгоритм:
            1. делаем GET-запрос с известными параметрами,
            указывая параметром lastname последний известный.
            lastname указывает на то, какой пункт нам уже известен.
            Система возвращает нам следующие опции.
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

                ДА, ЭТО ТАК КРИВО ВНУТРИ РАБОТАЕТ!)

    Arguments:
        url (str) : адрес СГО, который использует школа.
        province (str) : название района.
        city (str) : название населенного пункта.
        school (str) : название ОО.

    Raises:
        LoginformError : если какая-то из опций не существует/
                         написана с ошибкой/...

    Returns:
        (dict) : keys=('cid', 'sid', 'sft', 'pid', 'cn', 'scid')

    Examples:
        >>> await _loginform(
        ...     'https://sgo.cit73.ru/',
        ...     'Городской округ Ульяновск',
        ...     'Ульяновск, г.',
        ...     '"Луговская ОШ"',
        ... )
        {'cid': 2,'sid': 73, 'sft': 2, 'pid': -51, 'cn': 51, 'scid': 488}

    TODO`s:
        отрефакторить эту функцию.
    """
    queue = {'sid': 'pid', 'pid': 'cn', 'sft': 'scid'}
    userform = {'pid': province, 'cn': city, 'scid': school}

    loginform = await _prepareloginform(url)

    async with ClientSession() as session:

        for lastname in queue.keys():
            items = (await handle(await session.get(
                url=routes.WEBAPI.format(url, routes.LOGINFORM),
                params={**loginform, 'lastname': lastname},
            )))['items']

            for item in items:
                if item['name'] == userform[queue[lastname]]:
                    loginform.update({queue[lastname]: item['id']})
                    break

            else:
                raise LoginformError(userform[queue[lastname]])

    return loginform


async def _prepareloginform(url: str) -> dict:
    """Получение id страны и id субъекта, а также типа ОО.

    Note:
        cid и sid для каждого сайта константы, sid, к тому же уникальный,
        поэтому мы можем брать их, не зная информации о конкретной школе.

        sft используется 2 (общеобразовательная), т.к. подразумевается,
        что пользователь учится в обзеобразовательной школе.

    Arguments:
        url (str) : адрес СГО, который использует школа.

    Returns:
        (dict) : keys=('cid', 'sid', 'sft').

    Examples:
        >>> await _prepareloginform('https://sgo.cit73.ru/')
        {'cid': 2, 'sid': 73, 'sft': 2}
        >>> await _prepareloginform('https://edu.admoblkaluga.ru/')
        {'cid': 2, 'sid': 122, 'sft': 2}
    """
    async with ClientSession() as session:
        loginform = await handle(await session.get(
            url=routes.WEBAPI.format(url, routes.PREPARELOGINFORM),
        ))
        return {
            'cid': loginform['cid'],  # id страны
            'sid': loginform['sid'],  # id субъекта
            'sft': 2,  # тип ОО (2 - общеобразовательная)
        }
