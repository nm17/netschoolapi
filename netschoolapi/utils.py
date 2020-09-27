import pkg_resources
import netschoolapi


def get_user_agent() -> str:
    """User-Agent, используемый NetSchoolAPI.

    Returns:
        str -- User-Agent.

    Examples:
        >>> get_user_agent()
        httpx/0.15.3 (NetSchoolAPI/2.0.0; +https://github.com/nm17/netschoolapi)
    """
    httpx_version = pkg_resources.get_distribution('httpx').version
    api_version = netschoolapi.__version__
    return f'httpx/{httpx_version} (NetSchoolAPI/{api_version}; +https://github.com/nm17/netschoolapi)'
