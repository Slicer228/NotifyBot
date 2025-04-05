from typing import Callable, List
import asyncio
from src.db import DbFetcher
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
    __slots__ = ('_users', '_user_indexes', '_logger', '_db', '_callback')

    def __init__(self, logger: Logger, db: DbFetcher):
        self._user_indexes = dict()
        self._users: List[UserTasker] = []
        self._logger = logger
        self._db = db
        self._callback = None

    async def init_users(self, callback: Callable) -> None:
        # crucial method when bot is initialazing
        self._callback = callback
        async def init(users: List[User]):
            for user in users:
                self._users.append(UserTasker(
                    self._logger,
                    user,
                    self._callback,
                    await self._db.get_all_tasks(user.user_id)
                ))
                self._users[-1].start_polling()
                self._user_indexes[user.user_id] = len(self._users) - 1

        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(init(self._db.get_all_users()))
        except RuntimeError:
            try:
                asyncio.run(init(self._db.get_all_users()))
            except BaseException as e:
                self._logger.error(e)
                raise InternalError('Error while initializing users')

    async def add_user(self, user: User) -> None:
        await self._db.set_user(user)
        self._users.append(UserTasker(
            self._logger,
            user,
            self._callback,
            await self._db.get_all_tasks(user.user_id)
        ))
        self._users[-1].start_polling()

    async def add_task(self, user: User, task: Task) -> None:
        if not self._user_indexes.get(user.user_id, None):
            await self.add_user(user)
        await self._db.set_new_task(task)
        self._users[self._user_indexes[user.user_id]].signal(task, 2)

    async def remove_task(self, user: User, task: Task) -> None:
        if not self._user_indexes.get(user.user_id, None):
            await self.add_user(user)
        await self._db.set_new_task(task)
        self._users[self._user_indexes[user.user_id]].signal(task, 3)

    async def update_task(self, user: User, task: Task) -> None:
        if not self._user_indexes.get(user.user_id, None):
            await self.add_user(user)
        await self._db.set_new_task(task)
        self._users[self._user_indexes[user.user_id]].signal(task, 1)



