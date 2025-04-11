from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.routers.buttons import main_menu_kb
from src.routers.states import check_state, del_last_msg
from src.validator import User

_r = Router()

def format_to_week_day(week_day_num: int) -> str:
    match week_day_num:
        case 0:
            return 'Понедельник'
        case 1:
            return 'Вторник'
        case 2:
            return 'Среда'
        case 3:
            return 'Четверг'
        case 4:
            return 'Пятница'
        case 5:
            return 'Суббота'
        case 6:
            return 'Воскресенье'


def get_task_router(root: Bot) -> Router:

    @_r.message(F.text == 'Показать мои задачи')
    @check_state
    @del_last_msg(root)
    async def get_tasks(message: Message, state: FSMContext, *args, **kwargs):
        tasks = await root.tasker.get_task(User(
            user_id=message.from_user.id,
            username=message.from_user.username
        ))
        resp = ""
        for task in tasks:
            resp += f"Задача №{task.task_id}\nКогда: {format_to_week_day(task.week_day)} {task.hours}:{task.minutes}\n{task.description}\n\n"
        if resp:
            msg = await message.answer(resp, reply_markup=main_menu_kb)
        else:
            msg = await message.answer("У вас нет ни одной задачи :(", reply_markup=main_menu_kb)

        return msg.message_id

    return _r