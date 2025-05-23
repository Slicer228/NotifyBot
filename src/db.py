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
                        `task_id` INTEGER PRIMARY KEY AUTOINCREMENT,
                        `user_id` INTEGER NOT NULL,
                        `week_day` INTEGER NOT NULL,
                        `hours` INTEGER NOT NULL,
                        `minutes` INTEGER NOT NULL,
                        `is_one_time` BOOLEAN DEFAULT FALSE, 
                        `description` TEXT,
                    FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`)
                    );
                """
            )
            conn.execute(
                """
                    CREATE TABLE IF NOT EXISTS `msg_to_kill` (
                        `chat_id` INTEGER NOT NULL,
                        `msg_id` INTEGER NOT NULL
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
                INSERT INTO tasks(user_id, week_day, hours, minutes, is_one_time, description) VALUES(?, ?, ?, ?, ?, ?)
            """
            async with self.get_connection() as conn:
                await conn.execute(stmt, task())
                stmt = "SELECT last_insert_rowid()"
                cur = await conn.execute(stmt)
                new_id = await cur.fetchone()
                task.task_id = new_id[0]
                await conn.commit()
        except Exception as e:
            self._logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при добавлении задачи')

    async def remove_task(
            self,
            task: Task
    ) -> None:
        try:
            stmt = """
                DELETE FROM tasks
                WHERE task_id = ?
            """
            async with self.get_connection() as conn:
                await conn.execute(stmt, [task.task_id])
                await conn.commit()
        except Exception as e:
            self._logger.error(e)
            raise DatabaseError('Ошибка при работе с базой данных!\nОшибка при удалении задачи')

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
                    hours=x[3],
                    minutes=x[4],
                    is_one_time=x[5],
                    description=x[6],
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

    async def add_msg_to_kill(self, chat_id: int, msg_id: int) -> None:
        async with self.get_connection() as conn:
            stmt = """
                INSERT INTO msg_to_kill (chat_id, msg_id)
                VALUES (?, ?)
            """
            try:
                await conn.execute(stmt, [chat_id, msg_id])
                await conn.commit()
            except BaseException as e:
                self._logger.error(e)

    def clear_and_get_msg_to_kill(self) -> list:
        with sqlite3.connect(self._cfg.DB_NAME) as conn:
            stmt = """
                SELECT * FROM msg_to_kill
            """
            try:
                cur = conn.execute(stmt)
                data = cur.fetchall()
                stmt = """
                    DELETE FROM msg_to_kill
                """
                conn.execute(stmt)
                conn.commit()
                return data
            except BaseException as e:
                self._logger.error(e)




