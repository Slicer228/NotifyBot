from src.db import DbFetcher, DbInteractor
from src.exc import InternalError
from src.logger import Logger
from src.validator import User, Task


class UserTasker:
    __slots__ = ('_logger', '_user', '_tasks', '_db')

    def __init__(self, logger: Logger, user: User, db: DbInteractor):
        self._db = db
        self._logger = logger
        self._tasks = DbFetcher.get_all_tasks(user.user_id, self._logger, connection=self._db.get_connection())
        self._user = user







class UserTaskerFarm:
    __slots__ = ('_users', '_logger', '_db')

    def __init__(self, logger: Logger, db: DbInteractor):
        self._users = dict()
        self._users_updates = dict()
        self._logger = logger
        self._db = db

    async def add_user(self, user: User) -> None:
        try:
            self._users[user.id] = list()
            self._users_updates[user.id] = user.last_update
        except Exception as e:
            self._logger.error(e)
            raise InternalError('Ошибка при добавлении пользователя')

    async def add_task(self, user_id: User, task: Task) -> None:
        ...



