from marshmallow import EXCLUDE, Schema, fields


__all__ = ['Assignment', 'Attachment', 'Diary']


class NetSchoolAPISchema(Schema):
    class Meta:
        dateformat = '%Y-%m-%dT00:00:00'
        unknown = EXCLUDE


class Attachment(NetSchoolAPISchema):
    id = fields.Integer()
    name = fields.String(data_key='originalFileName')
    description = fields.String(allow_none=True, missing='')


class Assignment(NetSchoolAPISchema):
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
        missing=False,
        data_key='mark',
    )
    comment = fields.Function(
        deserialize=lambda mark_comment: mark_comment['name'],
        missing='',
        data_key='markComment',
    )
    deadline = fields.Date(data_key='dueDate')


class Lesson(NetSchoolAPISchema):
    day = fields.Date()
    start = fields.Time(data_key='startTime')
    end = fields.Time(data_key='endTime')
    room = fields.String()
    number = fields.Integer()
    subject = fields.String(data_key='subjectName')
    assignments = fields.List(fields.Nested(Assignment), missing=[])


class Day(NetSchoolAPISchema):
    day = fields.Date(data_key='date')
    lessons = fields.List(fields.Nested(Lesson))


class Diary(NetSchoolAPISchema):
    start = fields.Date(data_key='weekStart')
    end = fields.Date(data_key='weekEnd')
    schedule = fields.List(fields.Nested(Day), data_key='weekDays')
