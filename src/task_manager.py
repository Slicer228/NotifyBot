from src.exc import InternalError
from src.logger import Logger
from src.validator import User


class TaskFarm:
    __slots__ = ('_users', '_users_updates', '_logger')

    def __init__(self, logger: Logger):
        self._users = dict()
        self._users_updates = dict()
        self._logger = logger

    def add_user(self, user: User) -> None:
        try:
            self._users[user.id] = list()
            self._users_updates[user.id] = user.last_update
        except Exception as e:
            self._logger.error(e)
            raise InternalError('Ошибка при добавлении пользователя')



