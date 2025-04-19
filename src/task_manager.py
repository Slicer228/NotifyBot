from typing import Callable, List
import asyncio
from zoneinfo import ZoneInfo
from src.db import DbFetcher
from src.exc import InternalError
from src.logger import Logger
from src.validator import User, Task
from apscheduler.schedulers.background import BackgroundScheduler
tz = ZoneInfo('Europe/Moscow')


class UserTasker:
    __slots__ = ('_logger', '_user', '_tasks', '_db', '_callback', '_scheduler', '_signal')

    def __init__(self, logger: Logger, user: User, callback: Callable, tasks: List[Task]):
        self._logger = logger
        self._tasks: List[Task] = tasks
        self._user = user
        self._callback = callback
        self._scheduler = BackgroundScheduler(timezone=tz)
        self._signal = None

    def add_task(self, task: Task):
        self._scheduler.add_job(
            self._callback,
            'cron',
            [self._user.user_id, task, 2],
            id=f"{task.task_id}_l1",
            hour=8,
            minute=0,
            day_of_week=task.week_day,
        )
        self._scheduler.add_job(
            self._callback,
            'cron',
            [self._user.user_id, task, 2],
            id=f"{task.task_id}_l2",
            hour=task.hours-1,
            minute=task.minutes,
            day_of_week=task.week_day,
        )
        self._scheduler.add_job(
            self._callback,
            'cron',
            [self._user.user_id, task, 2],
            id=f"{task.task_id}_l3",
            hour=(task.hours if task.minutes >= 5 else task.hours-1),
            minute=(task.minutes - 5 if task.minutes >= 5 else (60 + task.minutes) - 5),
            day_of_week=task.week_day,
        )

    def remove_task(self, task: Task):
        self._scheduler.remove_job(f"{task.task_id}_l1")
        self._scheduler.remove_job(f"{task.task_id}_l2")
        self._scheduler.remove_job(f"{task.task_id}_l3")

    def signal(self, task: Task, stype: int) -> None:
        #1 - update; 2 - add; 3 - delete
        if stype == 1:
            try:
                self.remove_task(task)
                self.add_task(task)
            except LookupError as e:
                self._logger.error(e)
                raise InternalError('Task not found')
        elif stype == 2:
            self.add_task(task)
        elif stype == 3:
            try:
                self.remove_task(task)
            except LookupError as e:
                self._logger.error(e)
                raise InternalError('Task not found')
        else:
            raise InternalError('Invalid task type')

    def start_polling(self) -> None:
        for task in self._tasks:
            self.add_task(task)

        self._scheduler.start()


def user_exists(func):
    async def wrapper(self, user: User, *args):
        if not self._user_indexes.get(user.user_id, None):
            await self.add_user(user)
        return await func(self, user, *args)

    return wrapper


class UserTaskerFarm:
    __slots__ = ('_users', '_user_indexes', '_logger', '_db', '_callback_notify', '_scheduler', '_callback_delete')

    def __init__(self, logger: Logger, db: DbFetcher):
        self._user_indexes = dict()
        self._users: List[UserTasker] = []
        self._logger = logger
        self._db = db
        self._callback_notify = None
        self._callback_delete = None
        self._scheduler = BackgroundScheduler(timezone=tz)

    def init_users(self, callback_out: Callable, callback_in: Callable) -> None:
        # crucial method when bot is initialazing
        self._callback_notify = callback_out
        self._callback_delete = callback_in
        self._scheduler.add_job(
            self._del_yesterday_msgs,
            'cron',
            hour=0,
            minute=0,
        )
        self._scheduler.start()

        async def init(users: List[User]):
            for user in users:
                self._users.append(UserTasker(
                    self._logger,
                    user,
                    self._callback_notify,
                    await self._db.get_all_tasks(user.user_id)
                ))
                self._users[-1].start_polling()
                self._user_indexes[user.user_id] = len(self._users) - 1

        try:
            asyncio.run(init(self._db.get_all_users()))
        except BaseException as e:
            self._logger.error(e)
            raise InternalError('Error while initializing users')

    def _del_yesterday_msgs(self) -> None:
        msgs = self._db.clear_and_get_msg_to_kill()
        for msg in msgs:
            self._callback_delete(*msg)

    async def add_user(self, user: User) -> None:
        await self._db.set_user(user)
        self._users.append(UserTasker(
            self._logger,
            user,
            self._callback_notify,
            await self._db.get_all_tasks(user.user_id)
        ))
        self._users[-1].start_polling()

    @user_exists
    async def add_task(self, user: User, task: Task) -> None:
        await self._db.set_new_task(task)
        self._users[self._user_indexes[user.user_id]].signal(task, 2)

    @user_exists
    async def remove_task(self, user: User, task: Task) -> None:
        await self._db.remove_task(task)
        self._users[self._user_indexes[user.user_id]].signal(task, 3)

    @user_exists
    async def update_task(self, user: User, task: Task) -> None:
        await self.remove_task(user, task)
        await self.add_task(user, task)

    @user_exists
    async def get_task(self, user: User) -> List[Task]:
        return await self._db.get_all_tasks(user.user_id)



