# -*- coding: utf-8 -*-

"""Модуль для проверки ClientResponse`ов."""

from aiohttp import ClientResponse
from http import HTTPStatus

from utilities.exceptions import ResponseError

_Ok = HTTPStatus.OK.value  # <200>


async def handle(response: ClientResponse) -> dict:
    """Возвращает JSON, если код ответа == <200>, иначе выбрасывает исключение.

    Arguments:
        response (ClientResponse) : ответ сервера.

    Raises:
        ResponseError : если код ответа сервера != <200>.

    Returns:
        (dict) : JSON ответа сервера.
    """
    status = response.status
    if status != _Ok:
        raise ResponseError(status, (await response.json())['message'])
    return await response.json()
