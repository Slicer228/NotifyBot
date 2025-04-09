from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from src.validator import User
from src.routers.states import AddTask, GeneratedTask, DeclineChanges
from src.routers.states import del_last_msg, check_state, DeclineChanges


_r = Router()
week_days = [
    [InlineKeyboardButton(
        text="Понедельник",
        callback_data=GeneratedTask(
            week_day=0
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Вторник",
        callback_data=GeneratedTask(
            week_day=1
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Среда",
        callback_data=GeneratedTask(
            week_day=2
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Четверг",
        callback_data=GeneratedTask(
            week_day=3
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Пятница",
        callback_data=GeneratedTask(
            week_day=4
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Суббота",
        callback_data=GeneratedTask(
            week_day=5
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Воскресенье",
        callback_data=GeneratedTask(
            week_day=6
        ).pack()
    )],
    [InlineKeyboardButton(
        text="ОТМЕНА",
        callback_data=DeclineChanges().pack()
    )],
]
week_days_inline = InlineKeyboardMarkup(inline_keyboard=week_days)


def get_add_task_router(root) -> Router:

    @_r.message(F.text == 'Добавить задачу')
    @check_state
    @del_last_msg(root)
    async def add_task1(message: Message, state: FSMContext, *args, **kwargs):
        msg = await message.answer("Выберите день недели", reply_markup=week_days_inline)

        return msg.message_id
    return _r
