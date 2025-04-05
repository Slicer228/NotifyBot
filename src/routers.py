import asyncio
from typing import Literal

from aiogram.filters import Command
from aiogram.types import Message

import aiogram
from aiogram import Dispatcher

from src.config import Config
from src.exc import InternalError
from src.logger import Logger
from src.task_manager import UserTaskerFarm
from src.validator import Task, User

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
        @_dp.message(Command('start'))
        async def on_message(message: Message):
            try:
                await self._tasker.add_user(User(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                ))
                await message.answer('Welcome to notify bot!')
            except:
                await message.answer('Error on start')

        @_dp.message(Command('help'))
        async def on_message(message: Message):
            await message.answer('Help msg')

    def run(self):
        async def launch(dp: Dispatcher):
            await dp.start_polling(self)
        self.init_routers()
        asyncio.run(launch(_dp))

#delete
#add
#start
#list