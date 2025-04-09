import asyncio
from typing import Literal
import aiogram
from aiogram import Dispatcher
from src.config import Config
from src.exc import InternalError
from src.logger import Logger
from src.task_manager import UserTaskerFarm
from src.validator import Task, User
from src.routers.primary import get_primary_router
from src.routers.add_task import get_add_task_router


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
    __slots__ = ('cfg', 'tasker', 'logger', '_loop')
    _instance = None

    def __init__(self, logger: Logger = None, tasker: UserTaskerFarm = None, cfg: Config = None):
        super().__init__(cfg.BOT_TOKEN)
        if not logger or not tasker or not cfg:
            raise InternalError
        self.tasker = tasker
        self.tasker.init_users(self.notify)
        self.logger = logger
        self.cfg = cfg

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def notify(self, user_id: int, task: Task, notify_level: NotifyLevels):
        match notify_level:
            case 0:
                asyncio.run_coroutine_threadsafe(self.send_message(
                    user_id,
                    f"Уведомление №{task.task_id}\nУ вас сегодня в {task.hours}:{task.minutes}:\n{task.description}"
                ), self._loop)
            case 1:
                asyncio.run_coroutine_threadsafe(self.send_message(
                    user_id,
                    f"Уведомление №{task.task_id}\nЧерез 1 час у вас:\n{task.description}"
                ), self._loop)
            case 2:
                asyncio.run_coroutine_threadsafe(self.send_message(
                    user_id,
                    f"Уведомление №{task.task_id}\nЧерез 5 минут у вас:\n{task.description}"
                ), self._loop)
            case _:
                raise InternalError('Error in notify level')
        if task.is_one_time:
            asyncio.run_coroutine_threadsafe(
                self.tasker.remove_task(User(user_id=user_id), task),
                self._loop
            )

    def init_routers(self):
        _dp.include_routers(
            get_primary_router(self),
            get_add_task_router(self),
        )

    def run(self):
        async def launch(dp: Dispatcher):
            self._loop = asyncio.get_event_loop()
            await dp.start_polling(self)
        self.init_routers()
        asyncio.run(launch(_dp))

#delete
#add
#start
#list