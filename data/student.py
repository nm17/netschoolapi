# -*- coding: utf-8 -*-

"""Модуль, содержащий основной класс."""


class Student:
    """Основной класс. Взаимодействует с дневником."""

    _uid: int  # user id
    _yid: int  # year id
    _at: str

    def __init__(self, uid: int, yid: int, at: str) -> None:
        """Инициализатор.

        Arguments:
            uid (int) : id пользователя.
            yid (int) : id года (зачем, непонятно).
            at (str) : сессия.
        """
        self._uid = uid
        self._yid = yid
        self._at = at
