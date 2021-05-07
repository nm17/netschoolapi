from dataclasses import dataclass, fields
from datetime import date, time
from types import GenericAlias
from typing import Any, Optional, get_args, get_type_hints


__all__ = ['Assignment', 'School', 'diary', 'announcement']


@dataclass
class Attachment:
    id: int
    name: str
    description: str


@dataclass
class Announcement:
    name: str
    content: str
    post_date: date
    attachments: list[Attachment]


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
    room: str
    subject: str
    assignments: list[Assignment]


@dataclass
class Day:
    day: date
    lessons: list[Lesson]


@dataclass
class Diary:
    start: date
    end: date
    schedule: list[Day]


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


def _make_nested_dataclass(cls, field_values: dict[str, Any]):
    field_types = get_type_hints(cls)

    init_kwargs = {}
    for field in fields(cls):
        field_type = field_types[field.name]
        field_value = field_values[field.name]

        if isinstance(field_type, GenericAlias):
            datacls_name = get_args(field_type)[0]
            init_kwargs[field.name] = [
                _make_nested_dataclass(datacls_name, datacls_init_args)
                for datacls_init_args in field_value
            ]
        else:
            init_kwargs[field.name] = field_value

    return cls(**init_kwargs)


def diary(init_kwargs: dict[str, Any]) -> Diary:
    return _make_nested_dataclass(Diary, init_kwargs)


def announcement(init_kwargs: dict[str, Any]) -> Announcement:
    return _make_nested_dataclass(Announcement, init_kwargs)
