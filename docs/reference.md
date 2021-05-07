# Справочник

## Diary {#diary}

!!! Info
    В <<Сетевом городе>> дневник находится на `/angular/school/studentdiary/`.

Объекс класса `Diary` содержит три поля:

* `start: date` --- дата, с которой начинается дневник

```pycon
>>> diary.start
datetime.date(2021, 4, 19)
```

* `end: date` --- дата последнего дня в дневнике:

```pycon
>>> diary.end
datetime.date(2021, 4, 24)
```

* `schedule: list[Day]` --- список объектов [`Day`](#day):

```pycon
>>> diary.schedule
[Day(day=datetime.date(2021, 4, 22), lessons=[Lesson(...), ...]), ...]
```

## Day {#day}

Расписание одного дня с домашними заданиями и оценками. В классе два поля:

* `day: date`

```pycon
>>> wednesday = diary.schedule[2]
>>> wednesday.day
datetime.date(2021, 4, 21)
```

* `lessons: list[Lesson]` --- расписание на день:

```pycon
>>> wednesday.lessons
[Lesson(number=1, start=datetime.time(8, 30), ...), ...]
```

## Lesson {#lesson}

Поле `assignments` может содержать домашнее задание или оценку/отметку о задолженности.

Поля класса `Lesson`:

* `day: date` --- день, в который проходит урок
* `start: time` --- время начала урока
* `end: time` --- время окончания урока
* `number: int` --- номер урока в расписании
* `room: str` --- название кабинета, в котором проходит урок
* `subject: str` --- название предмета
* `assignments: list[Assignment]` --- домашнее задание, оценки и прочее

## Assignment {#assignment}

Из-за реализации <<Сетевого города>> домашние задания и оценки представляются одним классом с разным `typeId` и наличием поля `mark`. Поэтому нельзя отличить домашнее задание по русскому языку и отметку за контрольную по биологии, не посмотрев на <<тип>> и <<оценку>> объекта.

### Домашние задания и оценки {#homework-and-marks}

За оценки и просроченность заданий отвечают поля `mark` и `is_duty` соответственно.

#### Домашнее задание без оценки {#homework-without-mark}

```pycon
>>> day.lessons[0].assignments
[Assignment(type='Домашнее задание', subject='История', content='§§ 16–19', mark=None, ...), ...]
```

#### Оценка за самостоятельную работу {#independent-work-with-mark}

```pycon
>>> day.lessons[2].assignments
[Assignment(type='Самостоятельная работа', subject='Информатика', content='Написать NetSchoolAPI', mark=4, ...), ...]
```

#### Просроченное чтение наизусть {#overdue-recite}

```pycon
>>> day.lessons[5].assignments
[Assignment(type='Чтение наизусть', subject='Литература', content='«Блек энд Уайт» Маяковского', mark=None, is_duty=True, ...), ...]
```

!!! Note
    Задание может быть либо просрочено, либо за него может стоять оценка. Поэтому `mark` и `is_duty` не могут одновременно иметь значение. Если `is_duty=True`, то `mark=None`, как и наоборот, если `mark=4`, то `is_duty=False`.

#### Оценка за сочинение {#essay-with-mark}

```pycon
>>> day.lessons[3].assignments
[Assignment(type='Сочинение', subject='Литература', content='Моё отношение к Обломову', mark=5, ...), ...]
```

### Комментарии {#comments}

Комментарий --- сообщение от учителя ученику. На сайте <<Сетевого города>> комментарии отображаются как синие треугольнички возле оценок.

```pycon
>>> assignment = day.lessons[1].assignments
>>> assignment.comment
'Дописать сочинение до 4 февраля'
>>> # или если комментария к заданию нет:
>>> assignment.comment
''
```

## Announcement {#announcement}

!!! Note
    Объявления на сайте <<Сетевого города>> находятся на `/angular/school/announcements/`

Класс Announcement содержит 4 поля:

* `name: str` --- название
* `content: str` --- текст объявления
* `post_date: date` --- дата, когда объявление было загружено на сайт
* `attachments: list[Attachment]` --- приложения к объявлению


## Attachment {#attachment}

Приложенные файлы к урокам и объявлениям.

!!! Note
    Пока нет возможности скачивать приложенные файлы

* `id: int` --- поле используется, чтобы скачивать файлы, но пока библиотека такое не умеет
* `name: str` --- имя файла
* `description: str` --- короткое описание файла

## School {#school}

Контакты школы, адрес, руководящие должности и описание.

!!! Note
    Некоторые из полей могут быть незаполнены. Поля берутся из карточки на сайте <<Сетевого горда>>. Если вам нужна ещё информация оттуда --- [создайте](https://github.com/nm17/netschoolapi/issues) тему на гитхабе.

* `name` --- название школы
* `about` --- небольшое описание
* `address` --- юридический адрес
* `email`
* `site` --- УРЛ сайта школы
* `phone` --- контактный номер телефона
* `director` --- ФИО директора школы
* `AHC` --- заместителя по АХЧ
* `IT` --- по ИТ
* `UVR` --- по УВР
