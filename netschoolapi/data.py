from datetime import datetime, time
from typing import NamedTuple


class Lesson(NamedTuple):
    class_meeting_id: str = None
    day: datetime = None
    room: str = None
    start_time: time = None
    end_time: time = None
    subject_name: str = None

    @staticmethod
    def create(data):
        lesson = Lesson()
        lesson = lesson._replace(
            class_meeting_id=data["classmeetingId"]
        )  # https://stackoverflow.com/a/22562687
        lesson = lesson._replace(day=data["day"])
        lesson = lesson._replace(room=data["room"])
        lesson = lesson._replace(start_time=data["startTime"])
        lesson = lesson._replace(end_time=data["endTime"])
        lesson = lesson._replace(subject_name=data["subjectName"])
        return lesson
