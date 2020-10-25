from dataclasses import dataclass
from typing import List, Optional, Any


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
    name: Optional[str]
    originalFileName: str
    description: Optional[str]


@dataclass
class LessonAttachments:
    assignmentId: int
    attachments: List[Attachment]
    answerFiles: List[Any]


@dataclass
class AssignmentInfo:
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
class Assignment:
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
    assignments: Optional[List[Assignment]]


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


ASSIGNMENT_TYPES = {
    1: "Практическая работа",
    2: "Тематическая работа",
    3: "Домашнее задание",
    4: "Контрольная работа",
    5: "Самостоятельная работа",
    6: "Лабораторная работа",
    7: "Проект",
    8: "Диктант",
    9: "Реферат",
    10: "Ответ на уроке",
    11: "Сочинение",
    12: "Изложение",
    13: "Зачёт",
    14: "Тестирование",
    16: "Диагностическая контрольная работа",
    17: "Диагностическая работа",
    18: "Контрольное списывание",
    21: "Работа на уроке",
    22: "Работа в тетради",
    23: "Ведение рабочей тетради",
    24: "Доклад/Презентация",
    25: "Проверочная работа",
    26: "Чтение наизусть",
    27: "Пересказ текста",
    29: "Предметный диктант",
    31: "Дифференцированный зачет",
    32: "Работа с картами",
    33: "Экзамен",
    34: "Изложение с элементами сочинения",
    35: "Контроль аудирования",
    36: "Контроль грамматики",
    37: "Контроль лексеки",
    38: "Устный развернутый ответ",
}
