from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from src.routers.buttons import main_menu_kb, get_tasks_to_delete_kb, get_decide_cb
from src.routers.states import check_state, del_last_msg, DeleteTask, ToDeleteTask, StartDeleteTask
from src.validator import User, Task, MessageObj

_r = Router()


def get_del_task_router(root: Bot) -> Router:
    @_r.callback_query(StartDeleteTask.filter())
    @check_state
    @del_last_msg(root)
    async def add_task1(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        tasks = await root.tasker.get_task(User(
            user_id=cb.from_user.id,
            username=cb.from_user.username
        ))
        if len(tasks) == 0:
            return MessageObj(
                text="У вас нет ни одной задачи!",
                kb=main_menu_kb,
                chat_id=cb.from_user.id,
            )
        else:
            await state.set_state(DeleteTask.process)
            return MessageObj(
                text="Выберите номер задачи для удаления",
                kb=get_tasks_to_delete_kb(tasks),
                chat_id=cb.from_user.id,
            )

    @_r.callback_query(DeleteTask.process)
    @del_last_msg(root)
    async def del_task1(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        task = ToDeleteTask.unpack(cb.data)
        try:
            if task.decided is None:
                return MessageObj(
                    text=f'Вы уверены, что хотите удалить задачу №{task.task_id}?',
                    kb=get_decide_cb(task),
                    chat_id=cb.from_user.id,
                )
            elif not task.decided:
                await state.clear()
                return MessageObj(
                    text='Отмена удаления!\nВозврат к списку задач',
                    kb=get_tasks_to_delete_kb(
                        await root.tasker.get_task(User(
                            user_id=cb.from_user.id,
                            username=cb.from_user.username
                        ))
                    ),
                    chat_id=cb.from_user.id,
                )
            else:
                await root.tasker.remove_task(
                    User(
                        user_id=cb.from_user.id,
                        username=cb.from_user.username
                    ),
                    Task(
                        task_id=task.task_id
                    )
                )
                await state.clear()
                return MessageObj(
                    text=f'Задача №{task.task_id} успешно удалена!',
                    kb=get_tasks_to_delete_kb(
                        await root.tasker.get_task(User(
                            user_id=cb.from_user.id,
                            username=cb.from_user.username
                        ))
                    ),
                    chat_id=cb.from_user.id,
                )
        except Exception as e:
            await state.clear()
            return MessageObj(
                text='При удалении задачи что то пошло не так!',
                kb=main_menu_kb,
                chat_id=cb.from_user.id,
            )

    return _r
