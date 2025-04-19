import datetime

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
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
    user_id: Optional[int] = None
    week_day: Optional[int] = None
    hours: Optional[int] = None
    minutes: Optional[int] = None
    is_one_time: Optional[bool] = False
    description: Optional[str] = None

    def __call__(self) -> tuple:
        return self.user_id, self.week_day, self.hours, self.minutes, self.is_one_time, self.description


class User(BaseModel):
    user_id: int
    username: Optional[str] = None


class MessageObj(BaseModel):
    chat_id: Optional[int] = None
    text: Optional[str] = None
    kb: Optional[InlineKeyboardMarkup] = None
