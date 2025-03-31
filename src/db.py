import asyncio
import datetime
import os.path
import sqlite3
import sys
import threading
from time import sleep
from typing import List
import aiosqlite
from pydantic import ValidationError
from src.exc import DatabaseError, InternalValidationError, ExternalError
from src.logger import Logger
from src.config import Config
from src.validator import Task


s = threading.Semaphore(1)
_LOCK = threading.Lock()


class DbInteractor:
    __slots__ = ('_connection_pool', '_connection_pool_in_use', '_logger', '_cfg')

    def __init__(self, logger: Logger, cfg: Config) -> None:
        self._logger = logger
        try:
            self._cfg = cfg
            conn = sqlite3.connect(self._cfg.DB_NAME)
            self._connection_pool = list()
            self._connection_pool_in_use = list()
            for _ in range(int(self._cfg.DB_CONN_POOL_LIMIT)):
                self._connection_pool.append(sqlite3.connect(self._cfg.DB_NAME))
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS `users` (
                        `user_id` INTEGER NOT NULL UNIQUE,
                        `last_update` REAL NOT NULL
                    );
                """
            )
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS `tasks` (
                        `task_id` INTEGER AUTO_INCREMENT PRIMARY KEY,
                        `user_id` INTEGER NOT NULL,
                        `week_day` INTEGER NOT NULL,
                        `time` TEXT NOT NULL,
                        `description` TEXT,
                    FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`)
                    );
                """
            )
            conn.commit()
            conn.close()
        except BaseException as e:
            self._logger.error(e)
            self.close_all_connections()
            sys.exit(1)

    def get_connection(self) -> sqlite3.Connection | None:
        try:
            while True:
                if not self._connection_pool:
                    sleep(0.01)
                else:
                    _LOCK.acquire()
                    conn = self._connection_pool.pop(0)
                    self._connection_pool_in_use.append(conn)
                    _LOCK.release()
                    break

            yield conn
        except BaseException as e:
            self._logger.error(e)
        finally:
            _LOCK.acquire()
            self._connection_pool.append(conn)
            self._connection_pool_in_use.remove(conn)
            _LOCK.release()

    def close_all_connections(self) -> None:
        for conn in self._connection_pool + self._connection_pool_in_use:
            conn.close()
        self._connection_pool.clear()
        self._connection_pool_in_use.clear()



def user_activity(func):
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        _LOCK.acquire()
        kwargs['connection'].execute("""
            UPDATE `users`
            SET last_update = CURRENT_TIMESTAMP
        """)
        kwargs['connection'].commit()
        _LOCK.release()
        return data

    return wrapper


class DbFetcher:

    @staticmethod
    @user_activity
    def set_user(
            user_id: int,
            logger: Logger,
            connection: sqlite3.Connection = None
    ) -> None:
        try:
            stmt = """
                INSERT INTO users (user_id) VALUES(?)
            """

            connection.execute(stmt, [user_id])
            connection.commit()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении пользователя')

    @staticmethod
    @user_activity
    def set_new_task(
                task: Task,
                logger: Logger,
                connection: sqlite3.Connection = None
            ) -> None:
        try:
            stmt = """
                INSERT INTO tasks(user_id, week_day, time, description) VALUES(?, ?, ?, ?)
            """
            connection.execute(stmt, *task)
            connection.commit()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении задачи')

    @staticmethod
    def get_all_tasks(
            user_id: int,
            logger: Logger,
            connection: sqlite3.Connection = None
    ) -> List[Task]:
        try:
            stmt = """
                SELECT * FROM tasks
                WHERE user_id=?
            """

            cur: sqlite3.Cursor = connection.execute(stmt, [user_id])
            data = cur.fetchall()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при получении задач')

        try:
            data = list(map(
                lambda x: Task(
                    task_id=x[0],
                    user_id=x[1],
                    week_day=x[2],
                    time=x[3],
                    description=x[4],
                ),
                data
            ))
            return data
        except ValidationError as e:
            logger.error(e)
            raise InternalValidationError('Ошибка в полученных данных')

    @staticmethod
    def is_updated_recently(
            user_id: int,
            last_update: datetime.datetime,
            logger: Logger,
            connection: sqlite3.Connection = None
    ) -> bool:
        stmt = """
            SELECT last_update FROM users
            WHERE user_id=?
        """

        try:
            cur: sqlite3.Cursor = connection.execute(stmt, [user_id])
            data = cur.fetchone()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!')

        if data is None:
            raise ExternalError('Пользователь не существует!')

        if last_update < data[0]:
            return True
        return False


