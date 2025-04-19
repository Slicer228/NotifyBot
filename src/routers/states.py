from typing import Optional

from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from src.validator import Task, MessageObj


def del_last_msg(bot: Bot):
    def inner_decorator(func):
        async def wrapper(main_obj, state: FSMContext, *args, **kwargs):
            data = await state.get_data()
            last_msg_id = data.get("last_msg_id", None)
            msg: MessageObj = await func(main_obj, state, *args, **kwargs)
            if last_msg_id:
                try:
                    if msg.need_update:
                        await bot.delete_message(
                            chat_id=msg.chat_id,
                            message_id=last_msg_id
                        )
                        msg_ = await bot.send_message(
                            text=msg.text,
                            chat_id=msg.chat_id,
                            reply_markup=msg.kb
                        )
                        await state.update_data(last_msg_id=msg_.message_id)
                    else:
                        msg_ = await bot.edit_message_text(
                            text=msg.text,
                            chat_id=msg.chat_id,
                            reply_markup=msg.kb,
                            message_id=last_msg_id
                        )
                        await state.update_data(last_msg_id=msg_.message_id)
                except Exception as e:
                    if 'are exactly the same' not in str(e):
                        msg_ = await bot.send_message(
                            text=msg.text,
                            chat_id=msg.chat_id,
                            reply_markup=msg.kb
                        )
                        await state.update_data(last_msg_id=msg_.message_id)
            else:
                try:
                    msg_ = await bot.send_message(
                        text=msg.text,
                        chat_id=msg.chat_id,
                        reply_markup=msg.kb
                    )
                    await state.update_data(last_msg_id=msg_.message_id)
                except Exception as e:
                    bot.logger.error(e)

        return wrapper
    return inner_decorator


def check_state(func):
    async def wrapper(*args, state: FSMContext, **kwargs):
        if not await state.get_state():
            await func(*args, state, **kwargs)

    return wrapper


class StartDeleteTask(CallbackData, prefix="start_delete"):
    ...


class StartAddTask(CallbackData, prefix="start_add"):
    ...


class ShowTasks(CallbackData, prefix="show_tasks"):
    ...


class DeclineChanges(CallbackData, prefix="decline"):
    ...


class DeleteTask(StatesGroup):
    process = State()


class ToDeleteTask(CallbackData, prefix="end"):
    task_id: int
    decided: Optional[bool] = None


class AddTask(StatesGroup):
    week_day = State()
    hour = State()
    minute = State()
    is_one_time = State()
    description = State()


class GeneratedTask(CallbackData, prefix="task"):
    week_day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    is_one_time: Optional[bool] = None
    description: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if data := kwargs.get('description', None):
            if len(data) > 255:
                raise AttributeError("Description must be less than 255 characters")

    def __call__(self, user_id):
        return Task(
            user_id=user_id,
            week_day=self.week_day,
            hours=self.hour,
            minutes=self.minute,
            is_one_time=self.is_one_time,
            description=self.description
        )
