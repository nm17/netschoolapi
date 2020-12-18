from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, List

from dataclasses_json import dataclass_json, config, LetterCase


# Некоторые ключи пропущены, и это не ошибка.
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
    37: "Контроль лексики",
    38: "Устный развернутый ответ",
}

_ABSENCE_REASONS = {
    1: {'mark': 'ОТ', 'name': 'Отсутствовал'},
    2: {'mark': 'УП', 'name': 'Пропуск по уважительной причине'},
    3: {'mark': 'Б', 'name': 'Пропуск по болезни'},
    4: {'mark': 'НП', 'name': 'Пропуск по неуважительной причине'},
    5: {'mark': 'ОП', 'name': 'Опоздал'},
    6: {'mark': 'ОСВ', 'name': 'Освобожден'},
}

_DATETIME_DECODER = datetime.fromisoformat
_DATE_DECODER = lambda d: (datetime.fromisoformat(d).date())
_TIME_DECODER = time.fromisoformat


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Attachment:
    """Приложение. В терминах СГО: прикреплённый файл к домашнему заданию."""

    id: int
    file_name: str
    name: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class DetailedAssignment:
    id: int
    assignment_name: str
    activity_name: Optional[str]
    problem_name: Optional[str]
    subject: str = field(metadata=config(
        decoder=lambda s: s["name"], field_name="subjectGroup",
    ))
    is_deleted: bool
    day: date = field(metadata=config(decoder=_DATE_DECODER, field_name="date"))
    description: str
    teacher: str = field(metadata=config(decoder=lambda t: t["name"]))


@dataclass_json()
@dataclass(frozen=True)
class Assignment:
    """То же самое, что строчка в дневнике."""

    id: int
    type: str = field(metadata=config(
        decoder=lambda at: ASSIGNMENT_TYPES[at], field_name="typeId",
    ))
    name: str = field(metadata=config(field_name="assignmentName"))
    mark: Optional[int] = field(metadata=config(
        decoder=lambda m: m["mark"] if m else None,
    ))
    deadline: Optional[date] = field(metadata=config(
        decoder=_DATE_DECODER, field_name="dueDate",
    ))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Lesson:

    subject: str = field(metadata=config(field_name="subjectName"))
    day: date = field(metadata=config(decoder=_DATE_DECODER))
    starts_at: time = field(metadata=config(decoder=_TIME_DECODER, field_name="startTime"))
    ends_at: time = field(metadata=config(decoder=_TIME_DECODER, field_name="endTime"))
    number: int
    room: Optional[int]
    assignments: Optional[List[Assignment]] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class WeekDay:

    day: date = field(metadata=config(decoder=_DATE_DECODER, field_name="date"))
    lessons: List[Lesson]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Diary:

    week_start: date = field(metadata=config(decoder=_DATE_DECODER))
    week_end: date = field(metadata=config(decoder=_DATE_DECODER))
    schedule: List[WeekDay] = field(metadata=config(field_name="weekDays"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Announcement:
    id: int
    name: str
    description: str
    posted_at: date = field(metadata=config(decoder=_DATE_DECODER, field_name="postDate"))
    delete_date: Optional[date] = field(metadata=config(decoder=_DATE_DECODER))
    attachments: Optional[List[Attachment]] = field(default_factory=list)
