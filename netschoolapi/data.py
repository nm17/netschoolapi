from dataclasses import dataclass
from datetime import datetime, time
from typing import NamedTuple, List


@dataclass
class Lesson:
    class_meeting_id: str
    day: datetime
    room: str = None
    start_time: time = None
    end_time: time = None
    subject_name: str = None


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
