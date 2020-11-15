class NetSchoolAPIError(Exception):
    pass


class WrongIdentityError(NetSchoolAPIError):
    def __str__(self):
        return "Неправильный пароль или логин"


class SchoolAddressError(NetSchoolAPIError):
    def __init__(self, item: str):
        self._item = item

    def __str__(self):
        return f"Некорректное значение '{self._item}'"
