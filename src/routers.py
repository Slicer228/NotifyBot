import asyncio
from typing import Literal

from aiogram.types import Message

import aiogram
from aiogram import Dispatcher

from src.config import Config
from src.exc import InternalError
from src.logger import Logger
from src.task_manager import UserTaskerFarm
from src.validator import Task


_dp = Dispatcher()

MORNING = 0
HOUR_BEFORE = 1
FIVE_MINS_BEFORE = 2

NotifyLevels = Literal[
    MORNING: int,
    HOUR_BEFORE: int,
    FIVE_MINS_BEFORE: int
]


class Bot(aiogram.Bot):
    __slots__ = ('_cfg', '_tasker', '_logger')

    def __init__(self, logger: Logger, tasker: UserTaskerFarm, cfg: Config):
        super().__init__(cfg.BOT_TOKEN)
        self._tasker = tasker
        self._logger = logger
        self._cfg = cfg

    def notify(self, user_id: int, task: Task, notify_level: NotifyLevels):
        match notify_level:
            case 0:
                self.send_message(
                    user_id,
                    f"Уведомление №{task.task_id}\nУ вас сегодня в {task.hours}:{task.minutes}:\n{task.description}"
                )
            case 1:
                self.send_message(
                    user_id,
                    f"Уведомление №{task.task_id}\nЧерез час у вас:\n{task.description}"
                )
            case 2:
                self.send_message(
                    user_id,
                    f"Уведомление №{task.task_id}\nЧерез пять минут у вас:\n{task.description}"
                )
            case _:
                raise InternalError('Error in notify level')

    def init_routers(self):
        @_dp.message()
        async def on_message(message: Message):
            await message.answer('dsds')

    def run(self):
        async def launch(dp: Dispatcher):
            await dp.start_polling(self)
        self.init_routers()
        asyncio.run(launch(_dp))

#delete
#add
#start
#list