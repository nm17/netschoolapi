class WrongCredentialsError(Exception):
    pass


class RateLimitingError(Exception):
    pass


class UnknownServerError(Exception):
    pass


class UnknownLoginData(Exception):
    pass
