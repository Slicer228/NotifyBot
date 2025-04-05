from typing import Callable, List
import asyncio
from src.db import DbFetcher, LOCK
from src.exc import InternalError
from src.logger import Logger
from src.validator import User, Task
from apscheduler.schedulers.background import BackgroundScheduler


class UserTasker:
    __slots__ = ('_logger', '_user', '_tasks', '_db', '_callback', '_scheduler', '_signal')

    def __init__(self, logger: Logger, user: User, callback: Callable, tasks: List[Task]):
        self._logger = logger
        self._tasks: List[Task] = tasks
        self._user = user
        self._callback = callback
        self._scheduler = BackgroundScheduler()
        self._signal = None

    def signal(self, task: Task, stype: int) -> None:
        #1 - update; 2 - add; 3 - delete
        if stype == 1:
            try:
                self._scheduler.remove_job(str(task.id))
                self._scheduler.add_job(
                    self._callback,
                    'cron',
                    [task.description],
                    id=str(task.task_id),
                    hour=task.hours,
                    minute=task.minutes,
                    day_of_week=task.week_day,
                )
            except LookupError as e:
                self._logger.error(e)
                raise InternalError('Task not found')
        elif stype == 2:
            self._scheduler.add_job(
                self._callback,
                'cron',
                [self._user.user_id, task.description],
                id=str(task.task_id),
                hour=task.hours,
                minute=task.minutes,
                day_of_week=task.week_day,
            )
        elif stype == 3:
            try:
                self._scheduler.remove_job(str(task.id))
            except LookupError as e:
                self._logger.error(e)
                raise InternalError('Task not found')
        else:
            raise InternalError('Invalid task type')

    def start_polling(self) -> None:
        for task in self._tasks:
            self._scheduler.add_job(
                self._callback,
                'cron',
                [self._user.user_id, task.description],
                id=str(task.task_id),
                hour=task.hours,
                minute=task.minutes,
                day_of_week=task.week_day,
            )

        self._scheduler.start()


class UserTaskerFarm:
    __slots__ = ('_users', '_logger', '_db')

    def __init__(self, logger: Logger, db: DbFetcher):
        self._users = []
        self._logger = logger
        self._db = db

    async def init_users(self, callback: Callable) -> None:
        # crucial method when bot is initialazing
        async def init(users: List[User]):
            for user in users:
                self._users.append(UserTasker(
                    self._logger,
                    user,
                    callback,
                    await self._db.get_all_tasks(user.user_id)
                ))
                self._users[-1].start_polling()

        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(init(self._db.get_all_users()))
        except RuntimeError:
            try:
                asyncio.run(init(self._db.get_all_users()))
            except BaseException as e:
                self._logger.error(e)
                raise InternalError('Error while initializing users')

    async def add_user(self, user: User, callback: Callable) -> None:
        await self._db.set_user(user)
        async with LOCK:
            self._users.append(UserTasker(
                self._logger,
                user,
                callback,
                await self._db.get_all_tasks(user.user_id)
            ))
            self._users[-1].start_polling()

    async def add_task(self, user_id: User, task: Task) -> None:
        ...



