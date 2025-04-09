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


class Task(BaseModel):
    task_id: Optional[int] = None
    user_id: int
    week_day: int
    hours: int
    minutes: int
    is_one_time: bool = False
    description: Optional[str] = None

    def __call__(self) -> tuple:
        return self.user_id, self.week_day, self.hours, self.minutes, self.description


class User(BaseModel):
    user_id: int
    username: Optional[str] = None
