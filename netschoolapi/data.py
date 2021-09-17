import datetime
from dataclasses import dataclass, fields
from datetime import date, time
# noinspection PyUnresolvedReferences,PyProtectedMember
# because `_GenericAlias` is actually in `typing`
from typing import (
    Any, Optional, get_args, get_type_hints, Dict, List, _GenericAlias
)

__all__ = ['Assignment', 'School', 'diary', 'announcement']


@dataclass
class Attachment:
    id: int
    name: str
    description: Optional[str]


@dataclass
class Announcement:
    name: str
    content: str
    post_date: datetime.datetime
    attachments: List[Attachment]


@dataclass
class Assignment:
    id: int
    type: str
    content: str
    mark: Optional[int]
    is_duty: bool
    comment: str
    deadline: date


@dataclass
class Lesson:
    day: date
    start: time
    end: time
    number: int
    room: Optional[str]
    subject: str
    assignments: List[Assignment]


@dataclass
class Day:
    day: date
    lessons: List[Lesson]


@dataclass
class Diary:
    start: date
    end: date
    schedule: List[Day]


@dataclass
class School:
    name: str
    about: str
    address: str
    email: str
    site: str
    phone: str
    director: str
    AHC: str
    IT: str
    UVR: str


def _make_nested_dataclass(cls, field_values: Dict[str, Any]):
    """ In order to understand it, check the comments in function's body """
    field_types = get_type_hints(cls)

    init_kwargs = {}
    for field in fields(cls):  # field is of type dataclasses.Field
        field_type = field_types[field.name]  # dataclass field's type
        field_value = field_values[field.name]  # Field's value from json

        if (
            type(field_type) == _GenericAlias
            and field_type.__origin__ == list
        ):  # field: List[A]
            nested_dataclass = get_args(field_type)[0]  # List[A] -> A
            init_kwargs[field.name] = [
                _make_nested_dataclass(
                    cls=nested_dataclass,
                    field_values=dataclass_init_args
                )
                for dataclass_init_args in field_value
                # field_value now contains List[Dict[field_name, value]]
            ]
        else:  # field: int (that's an example)
            init_kwargs[field.name] = field_value

    return cls(**init_kwargs)


def diary(init_kwargs: Dict[str, Any]) -> Diary:
    return _make_nested_dataclass(Diary, init_kwargs)


def announcement(init_kwargs: Dict[str, Any]) -> Announcement:
    return _make_nested_dataclass(Announcement, init_kwargs)
