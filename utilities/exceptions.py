# -*- coding: utf-8 -*-

"""Ошибки, которые могут выбрасываться в ходе работы."""

from http import HTTPStatus


class ResponseError(Exception):
    def __init__(self, status: int, message: str) -> None:
        """Ошибка, возвращаемая сервером.

        Arguments:
            status (int) : код ошибки.
            message (str) : текст ошибки.
        """
        # noinspection PyArgumentList
        self._message = '<{0}> ({1}) : {2}'.format(
            status,  # код ошибки
            HTTPStatus(status).phrase,  # пояснение кода ошибки
            message,  # текст ошибки
        )

    def __str__(self) -> str:
        """Метод, возвращающий сообщение об ошибке.

        Returns:
            (str) : '<код ответа> (пояснение кода ответа) : текст ошибки'

        Examples:
            >>> raise ResponseError(409, 'Ошибка входа в систему.')
            Traceback (most recent call last):
              ...
            utilities.exceptions.ResponseError: <409> (Conflict) : Ошибка входа в систему.
        """
        return self._message


class LoginformError(Exception):
    def __init__(self, option: str) -> None:
        """Ошибка, возникающая при указании неверного адреса школы.

        Arguments:
            option (str) : неверная опция.
        """
        self._message = r'\'{0}\' is an invalid loginform option.'.format(option)

    def __str__(self) -> str:
        r"""Метод, возвращающий сообщение об ошибке.

        Returns:
            (str) : '\'неверная опция\'' is an invalid loginform option.'
        """
        return self._message
