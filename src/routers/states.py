from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from src.validator import Task


def del_last_msg(bot):
    def inner_decorator(func):
        async def wrapper(msg: Message, state: FSMContext, *args, **kwargs):
            data = await state.get_data()
            last_msg_id: int = data.get("last_msg_id", None)
            if last_msg_id:
                await bot.delete_message(msg.chat.id, last_msg_id)
            msg_id = await func(msg, state, *args, **kwargs)
            await state.update_data(last_msg_id=msg_id)
        return wrapper
    return inner_decorator


def check_state(func):
    async def wrapper(*args, state: FSMContext, **kwargs):
        if not await state.get_state():
            await func(*args, state, **kwargs)

    return wrapper


class AddTask(StatesGroup):
    week_day = State()
    hour = State()
    minute = State()
    is_one_time = State()
    description = State()


class GeneratedTask(CallbackData, prefix="task"):
    week_day: Optional[int]
    hour: Optional[int]
    minute: Optional[int]
    is_one_time: Optional[bool]
    description: Optional[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if data := kwargs.get('description', None):
            if len(data) > 255:
                raise AttributeError("Description must be less than 255 characters")

    def __call__(self):
        return Task(
            week_day=self.week_day,
            hour=self.hour,
            minute=self.minute,
            is_one_time=self.is_one_time,
            description=self.description
        )
