import datetime

from pydantic import BaseModel
from typing import Optional, Literal


MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

WeekDays = Literal[
    MONDAY: int,
    TUESDAY: int,
    WEDNESDAY: int,
    THURSDAY: int,
    FRIDAY: int,
    SATURDAY: int,
    SUNDAY: int
]


class Task(BaseModel):
    task_id: int
    user_id: int
    week_day: WeekDays
    hours: int
    minutes: int
    description: Optional[str]

    def __iter__(self):
        yield self.user_id
        yield self.week_day
        yield self.time
        yield self.description


class User(BaseModel):
    user_id: int
    username: str
