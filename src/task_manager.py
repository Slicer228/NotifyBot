from typing import Callable, List
from src.db import DbFetcher, DbInteractor
from src.exc import InternalError
from src.logger import Logger
from src.validator import User, Task
from apscheduler.schedulers.background import BackgroundScheduler


class UserTasker:
    __slots__ = ('_logger', '_user', '_tasks', '_db', '_callback', '_scheduler', '_signal')

    def __init__(self, logger: Logger, user: User, db: DbInteractor, callback: Callable):
        self._db = db
        self._logger = logger
        self._tasks: List[Task] = DbFetcher.get_all_tasks(user.user_id, self._logger, connection=self._db.get_connection())
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
                [task.description],
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
                [task.description],
                id=str(task.task_id),
                hour=task.hours,
                minute=task.minutes,
                day_of_week=task.week_day,
            )

        self._scheduler.start()


class UserTaskerFarm:
    __slots__ = ('_users', '_logger', '_db')

    def __init__(self, logger: Logger, db: DbInteractor):
        self._users = []
        self._logger = logger
        self._db = db

    async def add_user(self, user: User) -> None:
        try:
            ...
        except Exception as e:
            self._logger.error(e)
            raise InternalError('Error adding user')

    async def add_task(self, user_id: User, task: Task) -> None:
        ...



