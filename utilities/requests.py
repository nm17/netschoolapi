# -*- coding: utf-8 -*-

"""Модуль для POST-, GET-запросов."""

from aiohttp import ClientSession, ClientResponse
from aiohttp.web import HTTPOk

from utilities.exceptions import ResponseError


async def _handle_response(response: ClientResponse) -> None:
    """Обрабатывает response.

    Получает ClientResponse и, если код ответа не <200>, вызывает исключение ResponseError.

    Arguments:
        response (ClientResponse) : ответ сервера

    Raises:
        ResponseError : Если response.status != 200
    """
    status = response.status
    if status != HTTPOk.status_code:
        raise ResponseError(
            status,
            response.reason,
            (await response.json())['message'],
        )


async def get(url: str, params: dict) -> dict:
    """GET-запрос.

    Делает GET-запрос на переданный url.
    Возвращает JSON ответа, если запрос успешен,
    в противном случае выбрасывает исключение ResponseError.

    Arguments:
        url (str) : адрес для GET-запроса
        params (dict) : параметры, передаваемые в запросе

    Returns:
        (dict) : JSON ответа
    """
    async with ClientSession() as session:
        async with session.get(url, params=params) as response:
            await _handle_response(response)
            return await response.json()


async def post(url: str, data: dict, headers: dict) -> dict:
    """POST-запрос.

    Делает POST-запрос на переданный url с параметрами data изаголовками headers.
    Возвращает JSON ответа, если запрос успешен,
    в противном случае выбрасывает исключение ResponseError.

    Arguments:
        url (str) : адрес для POST-запроса
        data (dict) : параметры запроса
        headers (dict) : заголовки запроса

    Returns:
        (dict) : JSON ответа
    """
    async with ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            await _handle_response(response)
            return await response.json()
