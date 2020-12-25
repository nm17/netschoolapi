from json.decoder import JSONDecodeError

from httpx import Response

from .exceptions import NetSchoolAPIError


def _json_or_panic(response: Response) -> dict:
    try:
        return response.json()
    except JSONDecodeError:
        raise NetSchoolAPIError(
            f"{response.status_code}: {response.url.path}: {response.content}",
        ) from None
