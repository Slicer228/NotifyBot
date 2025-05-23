import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from src.validator import User, MessageObj
from src.routers.states import AddTask, GeneratedTask, DeclineChanges, StartAddTask, one_handler_in_time
from src.routers.states import edit_last_msg, check_state, DeclineChanges
from src.routers.buttons import week_days_inline, get_minutes_kb, get_hours_kb, get_is_one_time_kb, main_menu_kb


_r = Router()
_LOCK = asyncio.Lock()


def get_add_task_router(root: Bot) -> Router:

    @_r.callback_query(StartAddTask.filter())
    @check_state
    @edit_last_msg(root)
    @one_handler_in_time
    async def add_task1(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.week_day)
        return MessageObj(
            text="Выберите день недели",
            kb=week_days_inline,
            chat_id=cb.from_user.id,
        )

    @_r.callback_query(AddTask.week_day)
    @edit_last_msg(root)
    @one_handler_in_time
    async def add_task2(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.hour)
        return MessageObj(
            text="Выберите нужный час",
            kb=get_hours_kb(GeneratedTask().unpack(cb.data)),
            chat_id=cb.from_user.id,
        )

    @_r.callback_query(AddTask.hour)
    @edit_last_msg(root)
    @one_handler_in_time
    async def add_task3(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.minute)
        return MessageObj(
            text="Выберите минуту",
            kb=get_minutes_kb(GeneratedTask().unpack(cb.data)),
            chat_id=cb.from_user.id,
        )

    @_r.callback_query(AddTask.minute)
    @edit_last_msg(root)
    @one_handler_in_time
    async def add_task4(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.is_one_time)
        return MessageObj(
            text="Это единоразовая задача?",
            kb=get_is_one_time_kb(GeneratedTask().unpack(cb.data)),
            chat_id=cb.from_user.id,
        )

    @_r.callback_query(AddTask.is_one_time)
    @edit_last_msg(root)
    @one_handler_in_time
    async def add_task5(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.description)
        await state.update_data(task=GeneratedTask().unpack(cb.data))
        return MessageObj(
            text="Напишите в чат описание вашей задачи",
            chat_id=cb.from_user.id,
        )

    @_r.message(AddTask.description)
    @edit_last_msg(root)
    @one_handler_in_time
    async def add_task6(message: Message, state: FSMContext, *args, **kwargs):
        if len(message.text) > 255:
            return MessageObj(
                text="Слишком длинное описание!",
                kb=main_menu_kb,
                chat_id=message.from_user.id,
                need_update=True
            )
        else:
            task = (await state.get_data()).get('task', None)
            if not task:
                await state.clear()
                return MessageObj(
                    text="Что то пошло не так!",
                    kb=main_menu_kb,
                    chat_id=message.from_user.id,
                    need_update=True
                )
            else:
                task.description = message.text
                try:
                    await root.tasker.add_task(
                        User(
                            user_id=message.from_user.id,
                            username=message.from_user.username
                        ),
                        task(message.from_user.id)
                    )
                    await state.clear()
                    return MessageObj(
                        text='Ваша задача успешно добавлена!\nПереход в главное меню',
                        kb=main_menu_kb,
                        chat_id=message.from_user.id,
                        need_update=True
                    )
                except Exception as e:
                    await state.clear()
                    return MessageObj(
                        text='При добавлении задачи произошла ошибка!',
                        kb=main_menu_kb,
                        chat_id=message.from_user.id,
                        need_update=True
                    )

    return _r
