from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import List, Optional

from dataclasses_json import LetterCase, config, dataclass_json


_ASSIGNMENT_TYPES = {
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
    37: "Контроль лексики",
    38: "Устный развернутый ответ",
}

_ABSENCE_REASONS = (
    {"mark": "ОТ", "description": "Отсутствовал"},
    {"mark": "УП", "description": "Пропуск по уважительной причине"},
    {"mark": "Б", "description": "Пропуск по болезни"},
    {"mark": "НП", "description": "Пропуск по неуважительной причине"},
    {"mark": "ОП", "description": "Опоздал"},
    {"mark": "ОСВ", "description": "Освобожден"},
)


def _datetime(iso_datetime: str) -> Optional[datetime]:
    return datetime.fromisoformat(iso_datetime) if iso_datetime else None


def _time(iso_time: str) -> Optional[time]:
    return time.fromisoformat(iso_time) if iso_time else None


def _date(iso_datetime: str) -> Optional[date]:
    return datetime.fromisoformat(iso_datetime).date() if iso_datetime else None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Attachment:
    id: int
    file_name: str
    name: Optional[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class DetailedAssignment:
    id: int
    description: str
    subject: str = field(metadata=config(
        decoder=lambda subject: subject["name"],
        field_name="subjectGroup",
    ))
    assignment_name: str
    activity_name: Optional[str]
    problem_name: Optional[str]
    is_deleted: bool
    day: date = field(metadata=config(decoder=_date, field_name="date"))
    teacher: str = field(metadata=config(
        decoder=lambda teacher: teacher["name"],
    ))


@dataclass_json()
@dataclass(frozen=True)
class Assignment:
    id: int
    type: str = field(metadata=config(
        decoder=lambda assignment_type: _ASSIGNMENT_TYPES[assignment_type],
        field_name="typeId",
    ))
    name: str = field(metadata=config(field_name="assignmentName"))
    mark: Optional[int] = field(metadata=config(
        decoder=lambda mark: mark["mark"] if mark else None,
    ))
    deadline: Optional[date] = field(metadata=config(decoder=_date, field_name="dueDate"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Lesson:
    number: int
    subject: str = field(metadata=config(field_name="subjectName"))
    day: date = field(metadata=config(decoder=_date))
    starts_at: time = field(metadata=config(decoder=_time, field_name="startTime"))
    ends_at: time = field(metadata=config(decoder=_time, field_name="endTime"))
    room: Optional[int]
    assignments: Optional[List[Assignment]] = field(default_factory=list)

    @property
    def homework(self) -> Optional[str]:
        if self.assignments:
            for assignment in self.assignments:
                if assignment.type == _ASSIGNMENT_TYPES[3]:
                    return assignment.name
        return None

    # TODO: несколько оценок за один урок?
    @property
    def mark(self) -> Optional[int]:
        for assignment in self.assignments:
            if assignment.mark:
                return assignment.mark
        return None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class WeekDay:
    day: date = field(metadata=config(decoder=_date, field_name="date"))
    lessons: List[Lesson]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Diary:
    week_start: date = field(metadata=config(decoder=_date))
    week_end: date = field(metadata=config(decoder=_date))
    schedule: List[WeekDay] = field(metadata=config(field_name="weekDays"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Announcement:
    id: int
    name: str
    description: str
    posted_at: Optional[date] = field(metadata=config(decoder=_date, field_name="postDate"))
    delete_date: Optional[date] = field(metadata=config(decoder=_date))
    attachments: Optional[List[Attachment]] = field(default_factory=list)
