import pkg_resources
import netschoolapi
from typing import List
from .data import Day


def get_user_agent() -> str:
    httpx_version = pkg_resources.get_distribution("httpx").version
    api_version = netschoolapi.__version__
    return f"httpx/{httpx_version} (NetSchoolAPI/{api_version}; +https://github.com/nm17/netschoolapi)"


def to_dict(d):
    """
    Обратная функция dacite.from_dict
    :param d: dataclass or dict
    """
    if hasattr(d, "__dict__"):
        return to_dict(d.__dict__)

    for k, v in d.items():

        if isinstance(v, list):
            for index, item in enumerate(v):
                if hasattr(item, "__dict__"):
                    d[k][index] = to_dict(item.__dict__)

        if hasattr(v, "__dict__"):
            d[k] = to_dict(v.__dict__)

    return d


def take_possible_attachments(days: List[Day]) -> List[int]:

    result = []

    for day in days:
        for lesson in day.lessons:
            if lesson.assignments is not None:
                for assignment in lesson.assignments:
                    result.append(assignment.id)
            continue

    return result
