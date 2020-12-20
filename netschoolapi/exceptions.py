class NetSchoolAPIError(Exception):
    pass


class LoginDataError(NetSchoolAPIError):
    def __str__(self):
        return "Неправильный пароль или логин"


class LoginFormError(NetSchoolAPIError):
    # Для более «человечного» сообщения об ошибках
    _types_declensions = {
        "sid": "регион",
        "pid": "округ/район",
        "cn": "населённый пункт",
        "sft": "тип ОО",
        "scid": "школа",
    }

    def __init__(self, type_: str, name: str):
        self._type = type_
        self._name = name

    def __str__(self):
        return f"Отсутствует {self._types_declensions[self._type]} " \
               f"с названием «{self._name}»"
