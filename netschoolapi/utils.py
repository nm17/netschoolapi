from json.decoder import JSONDecodeError
from httpx import Response
from .exceptions import NetSchoolAPIError
from . import __version__

_USER_AGENT = f"NetSchoolAPI/{__version__}"


def _json_or_panic(response: Response) -> dict:
    try:
        return response.json()
    except JSONDecodeError:
        raise NetSchoolAPIError(f"{response.status_code}: {response.url}: {response.content}") from None
