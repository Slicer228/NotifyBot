from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from src.routers.buttons import main_menu_kb, get_tasks_to_delete_kb, get_decide_cb
from src.routers.states import check_state, del_last_msg, DeleteTask, ToDeleteTask
from src.validator import User, Task


_r = Router()


def get_del_task_router(root: Bot) -> Router:
    @_r.message(F.text == 'Удалить задачу')
    @check_state
    @del_last_msg(root)
    async def add_task1(message: Message, state: FSMContext, *args, **kwargs):
        tasks = await root.tasker.get_task(User(
            user_id=message.from_user.id,
            username=message.from_user.username
        ))
        if len(tasks) == 0:
            msg = await message.answer("У вас нет ни одной задачи!", reply_markup=main_menu_kb)
        else:
            await state.set_state(DeleteTask.process)
            msg = await message.answer("Выберите номер задачи для удаления", reply_markup=get_tasks_to_delete_kb(tasks))
        return msg.message_id

    @_r.callback_query(DeleteTask.process)
    @del_last_msg(root)
    async def del_task1(cb: CallbackQuery, state: FSMContext, *args, **kwargs):
        task = ToDeleteTask.unpack(cb.data)
        try:
            if task.decided is None:
                msg = await root.send_message(
                    cb.from_user.id,
                    f'Вы уверены, что хотите удалить задачу №{task.task_id}?',
                    reply_markup=get_decide_cb(task)
                )
            elif not task.decided:
                msg = await root.send_message(
                    cb.from_user.id,
                    'Отмена удаления!\nВозврат к списку задач',
                    reply_markup=get_tasks_to_delete_kb(
                        await root.tasker.get_task(User(
                            user_id=cb.from_user.id,
                            username=cb.from_user.username
                        ))
                    ))
                await state.clear()
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
                msg = await root.send_message(
                    cb.from_user.id,
                    f'Задача №{task.task_id} успешно удалена!',
                    reply_markup=get_tasks_to_delete_kb(
                        await root.tasker.get_task(User(
                            user_id=cb.from_user.id,
                            username=cb.from_user.username
                        ))
                    ))
                await state.clear()
        except Exception as e:
            print(e)
            msg = await root.send_message(
                cb.from_user.id,
                'При удалении задачи что то пошло не так!'
            )
            await state.clear()

        return msg.message_id

    return _r
