from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from src.validator import User
from src.routers.states import AddTask, GeneratedTask, DeclineChanges
from src.routers.states import del_last_msg, check_state, DeclineChanges
from src.routers.buttons import week_days_inline, get_minutes_kb, get_hours_kb, get_is_one_time_kb, main_menu_kb


_r = Router()


def get_add_task_router(root: Bot) -> Router:

    @_r.message(F.text == 'Добавить задачу')
    @check_state
    @del_last_msg(root)
    async def add_task1(message: Message, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.week_day)
        msg = await message.answer("Выберите день недели", reply_markup=week_days_inline)
        return msg.message_id

    @_r.callback_query(AddTask.week_day)
    @del_last_msg(root)
    async def add_task2(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.hour)
        msg = await root.send_message(
            cb.from_user.id,
            "Выберите нужный час",
            reply_markup=get_hours_kb(GeneratedTask().unpack(cb.data))
        )
        return msg.message_id

    @_r.callback_query(AddTask.hour)
    @del_last_msg(root)
    async def add_task3(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.minute)
        msg = await root.send_message(
            cb.from_user.id,
            "Выберите минуту",
            reply_markup=get_minutes_kb(GeneratedTask().unpack(cb.data))
        )
        return msg.message_id

    @_r.callback_query(AddTask.minute)
    @del_last_msg(root)
    async def add_task4(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.is_one_time)
        msg = await root.send_message(
            cb.from_user.id,
            "Это единоразовая задача?",
            reply_markup=get_is_one_time_kb(GeneratedTask().unpack(cb.data))
        )
        return msg.message_id

    @_r.callback_query(AddTask.is_one_time)
    @del_last_msg(root)
    async def add_task5(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        await state.set_state(AddTask.description)
        msg = await root.send_message(
            cb.from_user.id,
            "Напишите в чат описание вашей задачи"
        )
        await state.update_data(task=GeneratedTask().unpack(cb.data))
        return msg.message_id

    @_r.message(AddTask.description)
    @del_last_msg(root)
    async def add_task6(message: Message, state: FSMContext, *args, **kwargs):
        if len(message.text) > 255:
            msg = await message.answer("Слишком длинное описание!")
        else:
            task = (await state.get_data()).get('task', None)
            if not task:
                msg = await message.answer("Что то пошло не так!")
                await state.clear()
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
                    msg = await message.answer('Ваша задача успешно добавлена!\nПереход в главное меню', reply_markup=main_menu_kb)
                    await state.clear()
                except Exception as e:
                    msg = await message.answer('При добавлении задачи произошла ошибка!')
                    await state.clear()
        return msg.message_id

    return _r
