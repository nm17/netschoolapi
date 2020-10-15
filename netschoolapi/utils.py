import pkg_resources
import netschoolapi


def get_user_agent():
    httpx_version = pkg_resources.get_distribution("httpx").version
    api_version = netschoolapi.__version__
    return f"httpx/{httpx_version} (NetSchoolAPI/{api_version}; +https://github.com/nm17/netschoolapi)"


def from_dataclass(d):
    """
    Обратная функция dacite.from_dict
    :param d: dataclass or dict
    """
    if hasattr(d, "__dict__"):
        return from_dataclass(d.__dict__)

    for k, v in d.items():

        if isinstance(v, list):
            for index, item in enumerate(v):
                if hasattr(item, "__dict__"):
                    d[k][index] = from_dataclass(item.__dict__)

        if hasattr(v, "__dict__"):
            d[k] = from_dataclass(v.__dict__)

    return d