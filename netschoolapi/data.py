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
    37: "Контроль лексеки",
    38: "Устный развернутый ответ",
}

DATETIME_CONFIG = config(decoder=datetime.fromisoformat)
DATE_CONFIG = config(decoder=lambda d: (datetime.fromisoformat(d).date()))
TIME_CONFIG = config(decoder=time.fromisoformat)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Assignment:
    """Assignment...."""

    a_type: str = field(metadata=config(
        field_name="typeId",
        decoder=lambda at: ASSIGNMENT_TYPES[at],
    ))
    name: str = field(metadata=config(field_name="assignmentName"))
    mark: Optional[int] = field(
        metadata=config(decoder=lambda m: m["mark"] if m else None),
    )
    due_date: Optional[date] = field(metadata=DATE_CONFIG, default=None)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Lesson:
    """Lesson...."""

    subject: str = field(metadata=config(field_name="subjectName"))
    day: date = field(metadata=DATE_CONFIG)
    start_time: time = field(metadata=TIME_CONFIG)
    end_time: time = field(metadata=TIME_CONFIG)
    number: int
    # relay: int  # Даже не знаю, зачем он может быть нужен
    room: Optional[int]
    assignments: Optional[List[Assignment]] = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class WeekDay:
    """WeekDay...."""

    date: date = field(metadata=DATE_CONFIG)
    lessons: List[Lesson]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Diary:
    """Diary...."""

    week_start: date = field(metadata=DATE_CONFIG)
    week_end: date = field(metadata=DATE_CONFIG)
    week_days: List[WeekDay]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class Announcement:
    """Announcement...."""
    pass
