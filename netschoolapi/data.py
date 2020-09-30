from datetime import datetime
from dateutil.parser import isoparse
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from typing import List, Optional


_datetime_field = config(encoder=datetime.isoformat, decoder=isoparse)


@dataclass_json
@dataclass
class Assignment:
    # Некоторые ключи отсутствуют by design, это не опечатка
    _ASSIGNMENT_TYPES = {
        1: 'Практическая работа',
        2: 'Тематическая работа',
        3: 'Домашнее задание',
        4: 'Контрольная работа',
        5: 'Самостоятельная работа',
        6: 'Лабораторная работа',
        7: 'Проект',
        8: 'Диктант',
        9: 'Реферат',
        10: 'Ответ на уроке',
        11: 'Сочинение',
        12: 'Изложение',
        13: 'Зачёт',
        14: 'Тестирование',
        16: 'Диагностическая контрольная работа',
        17: 'Диагностическая работа',
        18: 'Контрольное списывание',
        21: 'Работа на уроке',
        22: 'Работа в тетради',
        23: 'Ведение рабочей тетради',
        24: 'Доклад/Презентация',
        25: 'Проверочная работа',
        26: 'Чтение наизусть',
        27: 'Пересказ текста',
        29: 'Предметный диктант',
        31: 'Дифференцированный зачет',
        32: 'Работа с картами',
        33: 'Экзамен',
        34: 'Изложение с элементами сочинения',
        35: 'Контроль аудирования',
        36: 'Контроль грамматики',
        37: 'Контроль лексеки',
        38: 'Устный развернутый ответ',
    }

    type: str = field(
        metadata=config(
            decoder=lambda type_id: Assignment._ASSIGNMENT_TYPES[type_id],
            field_name='typeId',
        )
    )
    mark: Optional[int] = field(
        metadata=config(
            decoder=lambda mark_dict: mark_dict['mark'] if mark_dict else None,
        )
    )
    content: str = field(metadata=config(field_name='assignmentName'))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Lesson:
    number: int
    subject: str = field(metadata=config(field_name='subjectName'))
    day: datetime = field(metadata=_datetime_field)
    start_at: str = field(metadata=config(field_name='startTime'))
    end_at: str = field(metadata=config(field_name='endTime'))
    room: str
    assignments: List[Assignment] = field(default_factory=list)

    def homework(self) -> Optional[str]:
        for assignment in self.assignments:
            if assignment.type == 'Домашнее задание':
                return assignment.content

    def mark(self) -> Optional[int]:
        for assignment in self.assignments:
            if assignment.mark:
                return assignment.mark


@dataclass_json
@dataclass
class Weekday:
    date: datetime = field(metadata=_datetime_field)
    lessons: List[Lesson]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Diary:
    week_start: datetime = field(metadata=_datetime_field)
    week_end: datetime = field(metadata=_datetime_field)
    week_days: List[Weekday]


@dataclass_json
@dataclass
class Attachment:
    id: int
    name: str
    file_name: str = field(metadata=config(field_name='originalFileName'))


@dataclass_json
@dataclass
class User:
    id: int
    fio: str
    nickname: str = field(metadata=config(field_name='nickName'))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Announcement:
    description: str
    author: User
    attachments: List[Attachment]
    id: int
    name: str
    em = None
    recipient_info = None
