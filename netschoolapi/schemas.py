from typing import Any

from marshmallow import EXCLUDE, Schema, fields, pre_load


__all__ = ['Attachment', 'Announcement', 'Assignment', 'Diary', 'School']


class NetSchoolAPISchema(Schema):
    class Meta:
        dateformat = '%Y-%m-%dT00:00:00'
        unknown = EXCLUDE


class Attachment(NetSchoolAPISchema):
    id = fields.Integer()
    name = fields.String(data_key='originalFileName')
    description = fields.String(allow_none=True, missing='')


class Announcement(NetSchoolAPISchema):
    name = fields.String()
    content = fields.String(data_key='description')
    post_date = fields.Date(data_key='postDate')
    attachments = fields.List(fields.Nested(Attachment), missing=[])


class Assignment(NetSchoolAPISchema):
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


class School(NetSchoolAPISchema):
    name = fields.String(data_key='fullSchoolName')
    about = fields.String(data_key='about')

    address = fields.String(data_key='juridicalAddress')
    email = fields.String(data_key='email')
    site = fields.String(data_key='web')
    phone = fields.String(data_key='phones')

    director = fields.String(data_key='director')
    AHC = fields.String(data_key='principalAHC')
    IT = fields.String(data_key='principalIT')
    UVR = fields.String(data_key='principalUVR')

    @pre_load
    def unwrap_nested_dicts(self, data: dict[str, Any], **_) -> dict[str, str]:
        data.update(data.pop('commonInfo'))
        data.update(data.pop('contactInfo'))
        data.update(data.pop('managementInfo'))
        return data
