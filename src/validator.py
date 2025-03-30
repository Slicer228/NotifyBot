from pydantic import BaseModel
from typing import Optional, Literal

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7

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
    user_id: int
    week_day: WeekDays
    time: int
    description: Optional[str]

    def __iter__(self):
        yield self.user_id
        yield self.week_day
        yield self.time
        yield self.description



