class NetSchoolAPIError(Exception):
    pass


class AuthError(NetSchoolAPIError):
    pass


class SchoolNotFoundError(NetSchoolAPIError):
    pass


class NoResponseFromServer(NetSchoolAPIError):
    pass
