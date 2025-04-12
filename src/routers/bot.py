import asyncio
from typing import Literal
import aiogram
from aiogram import Dispatcher
from src.config import Config
from src.db import DbFetcher
from src.exc import InternalError
from src.logger import Logger
from src.routers.get_task import get_task_router
from src.task_manager import UserTaskerFarm
from src.validator import Task, User
from src.routers.primary import get_primary_router
from src.routers.add_task import get_add_task_router


_dp = Dispatcher()


class Bot(aiogram.Bot):
    __slots__ = ('cfg', 'tasker', 'logger', '_loop')
    _instance = None

    def __init__(self, db: DbFetcher, logger: Logger = None, tasker: UserTaskerFarm = None, cfg: Config = None):
        super().__init__(cfg.BOT_TOKEN)
        if not logger or not tasker or not cfg:
            raise InternalError
        self.tasker = tasker
        self.tasker.init_users(self.notify, self.del_msg)
        self.logger = logger
        self.cfg = cfg
        self.db = db

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def notify(self, user_id: int, task: Task, notify_level: int):
        try:
            match notify_level:
                case 0:
                    f = asyncio.run_coroutine_threadsafe(self.send_message(
                        user_id,
                        f"Уведомление №{task.task_id}\nУ вас сегодня в {task.hours}:{task.minutes}:\n{task.description}"
                    ), self._loop)
                case 1:
                    f = asyncio.run_coroutine_threadsafe(self.send_message(
                        user_id,
                        f"Уведомление №{task.task_id}\nЧерез 1 час у вас:\n{task.description}"
                    ), self._loop)
                case 2:
                    f = asyncio.run_coroutine_threadsafe(self.send_message(
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
            msg = f.result()
            asyncio.run_coroutine_threadsafe(
                self.db.add_msg_to_kill(msg.from_user.id, msg.message_id),
                self._loop
            )
        except Exception as e:
            self.logger.critical(e)

    def del_msg(self, chat_id: int, msg_id: int):
        try:
            asyncio.run_coroutine_threadsafe(
                self.delete_message(chat_id, msg_id),
                self._loop
            )
        except Exception as e:
            self.logger.error(e)

    def init_routers(self):
        _dp.include_routers(
            get_primary_router(self),
            get_add_task_router(self),
            get_task_router(self),
        )

    def run(self):
        async def launch(dp: Dispatcher):
            self._loop = asyncio.get_event_loop()
            self.logger.info('Starting bot...')
            await dp.start_polling(self, close_bot_session=True, skip_updates=True)
        self.init_routers()
        asyncio.run(launch(_dp))

#delete
#add
#start
#list