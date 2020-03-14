class UnknownError(Exception):
    def __init__(
            self,
            errormessage: str
    ) -> None:
        self._message = f"Unknown error was occurred: {errormessage}"

    def __str__(self) -> str:
        return self._message


class ServerError(Exception):
    def __init__(
            self,
            statuscode: int,
            reason: str,
            errormessage: str
    ) -> None:
        self._message = f"<{statuscode}> ({reason}) : {errormessage}"

    def __str__(self) -> str:
        return self._message


class WrongCredentialsError(Exception):
    pass
