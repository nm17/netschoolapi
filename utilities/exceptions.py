# -*- coding: utf-8 -*-

"""Ошибки."""


class ResponseError(Exception):
    def __init__(self, status: int, reason: str, message: str) -> None:
        """Ошибка ответа сервера.

        Arguments:
            status (int) : статус ошибки сервера
            reason (str) : пояснение статуса ошибки
            message (str) : сообщение ошибки
        """
        self._message = '<{0}> ({1}) : {2}'.format(status, reason, message)

    def __str__(self) -> str:
        """Возвращает сообщение об ошибке.

        Returns:
            (str) : сообщение об ошибке
        """
        return self._message


class LoginformError(Exception):
    def __init__(self, option: str) -> None:
        """Ошибка указания положения школы?.

        Arguments:
            option (str) : как это назвать?
        """
        self._message = '\"{0}\" is a invalid loginform option'.format(option)

    def __str__(self) -> str:
        """Возвращает сообщение об ошибке.

        Returns:
            (str) : сообщение об ошибке
        """
        return self._message


class UnknownError(Exception):
    def __init__(self, message: str) -> None:
        """Неизвестная ошибка.

        Arguments:
            message (str) : текст ошибки
        """
        self._message = 'Unknown error was occurred: \"{0}\"'.format(message)

    def __str__(self) -> str:
        """Возвращает сообщение об ошибке.

        Returns:
            (str) : сообщение об ошибке
        """
        return self._message
