from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Assignment:
    # FIXME: оддержка оценок
    mark: Optional[dict]  # Optional[int]
    typeId: int  # 3 -- ДЗ, 10 -- оценка. Пока всё.
    assignmentName: str


@dataclass
class Lesson:
    classmeetingId: int
    day: str
    number: int
    # relay: int. Что это значит?
    room: str
    startTime: str
    endTime: str
    subjectName: str
    assignments: Optional[List[Assignment]]


@dataclass
class Weekday:
    date: str
    lessons: List[Lesson]


@dataclass
class Diary:
    weekStart: str
    weekEnd: str
    weekDays: List[Weekday]


@dataclass
class Attachment:
    id: int
    name: str
    originalFileName: str


@dataclass
class User:
    id: int
    fio: str
    nickName: str


@dataclass
class Announcement:
    description: str
    author: User
    attachments: List[Attachment]
    id: int
    name: str
    em = None
    recipientInfo = None
