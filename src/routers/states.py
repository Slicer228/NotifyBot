from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message


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


class DecorForm(StatesGroup):
    last_msg_id = State()
