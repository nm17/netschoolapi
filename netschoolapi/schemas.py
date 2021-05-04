from marshmallow import Schema, EXCLUDE, fields


_DATE_FORMAT_STRING = '%Y-%m-%dT00:00:00'


class Attachment(Schema):
    id = fields.Integer()
    name = fields.String(data_key='originalFileName')
    description = fields.String(allow_none=True, missing='')

    class Meta:
        unknown = EXCLUDE


class Assignment(Schema):
    id = fields.Integer()
    type = fields.Function(
        deserialize=lambda type_id, context: context['assignment_types'][type_id],
        data_key='typeId',
    )
    content = fields.String(data_key='assignmentName')
    mark = fields.Function(
        deserialize=lambda mark_dict: mark_dict['mark'],
        allow_none=True,
        data_key='mark',
    )
    is_duty = fields.Function(
        deserialize=lambda mark_dict: mark_dict['dutyMark'],
        allow_none=True,
        data_key='mark',
    )
    comment = fields.Function(
        deserialize=lambda mark_comment: mark_comment['name'],
        missing='',
        data_key='markComment',
    )
    deadline = fields.Date(format=_DATE_FORMAT_STRING, data_key='dueDate')

    class Meta:
        unknown = EXCLUDE


class Lesson(Schema):
    day = fields.Date(format=_DATE_FORMAT_STRING)
    start = fields.Time(data_key='startTime')
    end = fields.Time(data_key='endTime')
    room = fields.String()
    number = fields.Integer()
    subject = fields.String(data_key='subjectName')
    assignments = fields.List(fields.Nested(Assignment), missing=[])

    class Meta:
        unknown = EXCLUDE


class Day(Schema):
    day = fields.Date(format=_DATE_FORMAT_STRING, data_key='date')
    lessons = fields.List(fields.Nested(Lesson))

    class Meta:
        unknown = EXCLUDE


class Diary(Schema):
    start = fields.Date(format=_DATE_FORMAT_STRING, data_key='weekStart')
    end = fields.DateTime(format=_DATE_FORMAT_STRING, data_key='weekEnd')
    schedule = fields.List(fields.Nested(Day), data_key='weekDays')

    class Meta:
        unknown = EXCLUDE
