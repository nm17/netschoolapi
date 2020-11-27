from json.decoder import JSONDecodeError
from httpx import Response
from .exceptions import NetSchoolAPIError

# User-Agent, используемый netschoolapi
# TODO auto version
_USER_AGENT = "NetSchoolAPI/4.0.0"


def _json_or_panic(response: Response) -> dict:
    try:
        return response.json()
    except JSONDecodeError:
        raise NetSchoolAPIError(f"{response.status_code}: {response.url}: {response.content}") from None
