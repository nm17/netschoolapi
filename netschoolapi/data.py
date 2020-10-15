from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LoginFormData:
    CID: int
    SID: int
    PID: int
    CN: int
    SFT: int
    SCID: int


@dataclass
class Mark:
    assignmentId: int
    studentId: int
    mark: Optional[int]
    dutyMark: bool


@dataclass
class SubjectGroup:
    id: int
    name: str


@dataclass
class User:
    id: int
    fio: str
    nickName: str


@dataclass
class Teacher:
    id: int
    name: str


@dataclass
class Attachment:
    id: int
    name: str
    originalFileName: str
    description: Optional[str]


@dataclass
class AssignmentsInfo:
    id: int
    assignmentName: str
    activityName: Optional[str]
    problemName: Optional[str]
    subjectGroup: SubjectGroup
    teacher: Teacher
    productId: Optional[int]
    isDeleted: bool
    weight: int
    date: str
    description: str
    attachments: List[Attachment]


@dataclass
class Assignments:
    mark: Optional[Mark]
    id: int
    typeId: int
    assignmentName: str
    dueDate: str
    weight: int


@dataclass
class Lesson:
    classmeetingId: int
    day: str
    number: int
    room: Optional[str]
    relay: int
    startTime: Optional[str]
    endTime: Optional[str]
    subjectName: Optional[str]
    assignments: Optional[List[Assignments]]


@dataclass
class Day:
    date: str
    lessons: List[Lesson]


@dataclass
class Diary:
    weekStart: str
    weekEnd: str
    weekDays: List[Day]
    termName: str
    className: str


@dataclass
class Announcement:
    description: str
    postDate: str
    deleteDate: Optional[str]
    author: User
    attachments: List[Attachment]
    id: int
    name: str
    recipientInfo: Optional[str]
