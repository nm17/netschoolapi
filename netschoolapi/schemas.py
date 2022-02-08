from typing import Any, Dict

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
    post_date = fields.DateTime(data_key='postDate')
    attachments = fields.List(fields.Nested(Attachment), missing=[])


class Assignment(NetSchoolAPISchema):
    id = fields.Integer()
    type = fields.Function(
        deserialize=(
            lambda type_id, context: context['assignment_types'][type_id]
        ),
        data_key='typeId',
    )
    content = fields.String(data_key='assignmentName')
    mark = fields.Integer(allow_none=True, data_key='mark')
    is_duty = fields.Boolean(data_key='dutyMark')
    comment = fields.Function(
        deserialize=lambda mark_comment: mark_comment['name'],
        missing='',
        data_key='markComment',
    )
    deadline = fields.Date(data_key='dueDate')

    @pre_load
    def unwrap_marks(self, assignment: Dict[str, Any], **_) -> Dict[str, str]:
        mark = assignment.pop('mark', None)
        if mark:
            assignment.update(mark)
        else:
            assignment.update({'mark': None, 'dutyMark': False})
        return assignment


class Lesson(NetSchoolAPISchema):
    day = fields.Date()
    start = fields.Time(data_key='startTime')
    end = fields.Time(data_key='endTime')
    room = fields.String(missing='', allow_none=True)
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

    address = fields.String(data_key='address')
    email = fields.String(data_key='email')
    site = fields.String(data_key='web')
    phone = fields.String(data_key='phones')

    director = fields.String(data_key='director')
    AHC = fields.String(data_key='principalAHC')
    IT = fields.String(data_key='principalIT')
    UVR = fields.String(data_key='principalUVR')

    @pre_load
    def unwrap_nested_dicts(
            self, school: Dict[str, Any], **_) -> Dict[str, str]:
        school.update(school.pop('commonInfo'))
        school.update(school.pop('contactInfo'))
        school.update(school.pop('managementInfo'))
        school['address'] = school['juridicalAddress'] or school['postAddress']
        return school
