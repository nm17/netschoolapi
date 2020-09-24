import pytest

from netschoolapi.utils import get_user_agent


def test_user_agent():
    ua = get_user_agent()

    assert "NetSchoolAPI" in ua
    assert "httpx" in ua
