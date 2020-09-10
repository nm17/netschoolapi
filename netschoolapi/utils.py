import pkg_resources
import netschoolapi


def get_user_agent():
    httpx_version = pkg_resources.get_distribution("httpx").version
    api_version = netschoolapi.__version__
    return f"httpx/{httpx_version} (NetSchoolAPI/{api_version}; +https://github.com/nm17/netschoolapi)"
