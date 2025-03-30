import asyncio
import os.path
import sqlite3
import sys
from typing import List

import aiosqlite
from pydantic import ValidationError

from src.exc import DatabaseError, InternalValidationError
from src.logger import Logger
from src.config import Config
from src.validator import Task

_LOCK = asyncio.Lock()


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
                self._connection_pool.append(aiosqlite.connect(self._cfg.DB_NAME))
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

    async def get_connection(self) -> aiosqlite.Connection | None:
        try:
            async with _LOCK:
                while not self._connection_pool:
                    await asyncio.sleep(0.01)
                conn = self._connection_pool.pop(0)
                self._connection_pool_in_use.append(conn)

            yield conn
        except BaseException as e:
            self._logger.error(e)
        finally:
            async with _LOCK:
                self._connection_pool.append(conn)
                self._connection_pool_in_use.remove(conn)

    def close_all_connections(self) -> None:
        async def close_all_connections():
            for conn in self._connection_pool:
                await conn.close()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(close_all_connections())
            return

        if not loop.is_running():
            asyncio.run(close_all_connections())
            return

        loop.run_until_complete(close_all_connections())


def user_activity(func):
    async def wrapper(*args, **kwargs):
        data = await func(*args, **kwargs)
        async with _LOCK:
            await kwargs['connection'].execute("""
                UPDATE `users`
                SET last_update = CURRENT_TIMESTAMP
            """)
            await kwargs['connection'].commit()
        return data

    return wrapper


class DbFetcher:

    @staticmethod
    @user_activity
    async def set_user(user_id: int, connection: aiosqlite.Connection, logger: Logger) -> None:
        try:
            stmt = """
                INSERT INTO users (user_id) VALUES(?)
            """

            await connection.execute(stmt, [user_id])
            await connection.commit()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении пользователя')

    @staticmethod
    @user_activity
    async def set_new_task(task: Task, connection: aiosqlite.Connection, logger: Logger) -> None:
        try:
            stmt = """
                INSERT INTO tasks(user_id, week_day, time, description) VALUES(?, ?, ?, ?)
            """
            await connection.execute(stmt, *task)
            await connection.commit()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении задачи')

    @staticmethod
    async def get_all_tasks(user_id: int, connection: aiosqlite.Connection, logger: Logger) -> List[Task]:
        try:
            stmt = """
                SELECT * FROM tasks
                WHERE user_id=?
            """

            cur: aiosqlite.Cursor = await connection.execute(stmt, user_id)
            data = await cur.fetchall()
        except Exception as e:
            logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при получении задач')

        try:
            data = list(map(
                lambda x: Task(
                    user_id=x[0],
                    week_day=x[1],
                    time=x[2],
                    description=x[3],
                ),
                data
            ))
            return data
        except ValidationError as e:
            logger.error(e)
            raise InternalValidationError('Ошибка в полученных данных')




