# -*- coding: utf-8 -*-

"""Модуль для запросов к сетевому API СГО."""

from utilities import requests
from utilities.exceptions import LoginformError


# поддомены сетового API СГО
_webapi = '/webapi'

_logindata = '/auth/getdata'

_prepareloginform = '/prepareloginform'
_loginform = '/loginform'

_login = '/login'

_referer = '/about.html'


async def prepareloginform(url: str) -> dict:
    """Получение необработанного loginform.

    Получение кодов страны и области, уникальных для каждого сайта,
    а также тип ОО, стандартный для всех сайтов.

    Note:
        'cid' (country id) : код страны
        'sid' (state id) : код области
        'sft' (school function ?) : тип ОО

    Arguments:
        url (str) : адрес сайта электронного дневника

    Returns:
        (dict) : код страны, код области и тип ОО

    Examples:
        >>> await prepareloginform('https://sgo.cit73.ru/')
        {'cid': 2, 'sid': 73, 'sft': 2}
    """
    loginform_ = await requests.get(url=url + _webapi + _prepareloginform, params={})
    return {
        'cid': loginform_['cid'],
        'sid': loginform_['sid'],
        'sft': 2,
    }


async def loginform(url: str, province: str, city: str, school: str) -> dict:
    """Получение обработанного loginform.

    Получение кодов страны и области, уникальных для каждого сайта,
    типа ОО, стандартного для всех сайтов,
    а также кодов района, города и школы.

    Note:
        ВСЕ АРГУМЕНТЫ НУЖНО ВВОДИТЬ В ТОЧНОСТИ КАК НА САЙТЕ!

        'pid' (province id) : код региона
        'cn' (city number) : код города
        'scid' (school id) : код школы

    Arguments:
        url (str) : адрес сайта электронного дневника
        province (str) : название района
        city (str) : название города
        school (str) : название школы

    Raises:
        LoginformError : при указании неверных данных школы

    Returns:
        (dict) : loginform ('cid', 'sid', 'sft', 'pid', 'cn', 'scid')

    Examples:
        >>> await loginform('https://sgo.cit73.ru', 'Городской округ Ульяновск', 'Ульяновск, г.', '"Луговская ОШ"')
        {'cid': 2,'sid': 73, 'sft': 2, 'pid': -51, 'cn': 51, 'scid': 488}

    TODO`s:
        Отрефакторить эту функцию
    """
    form = {'pid': province, 'cn': city, 'scid': school}
    queue = {'sid': 'pid', 'pid': 'cn', 'sft': 'scid'}

    loginform_ = await prepareloginform(url)

    for lastname in queue.keys():
        items = (await requests.get(
            url=url + _webapi + _loginform,
            params={**loginform_, 'lastname': lastname},
        ))['items']

        for item in items:
            if item['name'] == form[queue[lastname]]:
                loginform_.update({queue[lastname]: item['id']})
                break

        else:
            raise LoginformError(form[queue[lastname]])

    return loginform_


async def logindata(url: str) -> tuple:
    """Получние словаря уникальных значений, использующихся для входа.

    Note:
        lt, ver, salt - уникальны для каждого обращения.
                        Эти значения используются для входа в СГО.

    Arguments:
        url (str) : адрес сайта электронного дневника

    Returns:
        (dict) : уникальные значения lt, ver, salt

    Example:
        >>> await logindata('https://sgo.cit73.ru/')
        ('900630558', '686652767', '36357372362')
    """
    logindata_ = await requests.post(url=url + _webapi + _logindata, data={}, headers={})
    return logindata_['lt'], logindata_['ver'], logindata_['salt']


async def login(url: str, data: dict) -> dict:
    """Вход на сайт СГО.

    Arguments:
        url (str) : адрес сайта электронного дневника
        data (dict) : аргументы для входа (логин, пароль, loginform)

    Returns:
        (dict) : информация о сессии
    """
    return await requests.post(
        url=url + _webapi + _login,
        data=data,
        headers={'referer': url + _referer},
    )
