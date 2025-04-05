import asyncio
import sqlite3
import sys
from contextlib import asynccontextmanager
from time import sleep
from typing import List
import aiosqlite
from pydantic import ValidationError
from src.exc import DatabaseError, InternalValidationError, ExternalError, InternalError
from src.logger import Logger
from src.config import Config
from src.validator import Task, User


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

            async def generate_conns():
                for _ in range(int(self._cfg.DB_CONN_POOL_LIMIT)):
                    self._connection_pool.append(await aiosqlite.connect(self._cfg.DB_NAME))

            asyncio.run(generate_conns())

            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS `users` (
                        `user_id` INTEGER NOT NULL UNIQUE,
                        `username` TEXT NOT NULL
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

    @asynccontextmanager
    async def get_connection(self) -> aiosqlite.Connection | None:
        try:
            async with _LOCK:
                while True:
                    if not self._connection_pool:
                        await asyncio.sleep(0.01)
                    else:
                        conn = self._connection_pool.pop(0)
                        self._connection_pool_in_use.append(conn)
                        break

            yield conn
        except BaseException as e:
            self._logger.error(e)
        finally:
            async with _LOCK:
                self._connection_pool.append(conn)
                self._connection_pool_in_use.remove(conn)

    def close_all_connections(self) -> None:
        async def close_conns():
            for conn in self._connection_pool:
                await conn.close()

        try:
            loop = asyncio.get_running_loop()
            loop.run_until_complete(close_conns())
            self._connection_pool.clear()
            self._connection_pool_in_use.clear()
        except RuntimeError:
            try:
                asyncio.run(close_conns())
                self._connection_pool.clear()
                self._connection_pool_in_use.clear()
            except BaseException as e:
                self._logger.error(e)
                raise InternalError('Error while closing connections')


class DbFetcher(DbInteractor):

    async def set_user(
            self,
            user: User
    ) -> None:
        try:
            async with self.get_connection() as conn:
                stmt = """
                    SELECT * FROM users
                    WHERE user_id = ?
                """

                cur = await conn.execute(stmt, (user.user_id,))
                row = await cur.fetchone()
                if row:
                    return

                stmt = """
                    INSERT INTO users (user_id, username) VALUES(?, ?)
                """

                await conn.execute(stmt, [user.user_id, user.username])
                await conn.commit()
        except Exception as e:
            self._logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении пользователя')

    async def set_new_task(
                self,
                task: Task
            ) -> None:
        try:
            stmt = """
                INSERT INTO tasks(user_id, week_day, time, description) VALUES(?, ?, ?, ?)
            """
            async with self.get_connection() as conn:
                await conn.execute(stmt, *task)
                await conn.commit()
        except Exception as e:
            self._logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении задачи')

    async def get_all_tasks(
            self,
            user_id: int,
    ) -> List[Task]:
        try:
            stmt = """
                SELECT * FROM tasks
                WHERE user_id=?
            """
            async with self.get_connection() as conn:
                cur: aiosqlite.Cursor = await conn.execute(stmt, [user_id])
                data = await cur.fetchall()
        except Exception as e:
            self._logger.error(e)
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
            self._logger.error(e)
            raise InternalValidationError('Ошибка в полученных данных')

    def get_all_users(self) -> List[User]:
        with sqlite3.connect(self._cfg.DB_NAME) as conn:
            cur = conn.execute("""
                SELECT * FROM users
            """)

            data = cur.fetchall()

            return [User(user_id=u[0], username=u[1]) for u in data]



