import asyncio
import os.path
import sqlite3
import sys
import aiosqlite
from src.logger import Logger
from src.config import Config


class DbInteractor:
    __slots__ = ('_connection_pool', '_connection_pool_in_use', '_logger', '_cfg', '_lock')

    def __init__(self, logger: Logger, cfg: Config):
        self._logger = logger
        try:
            self._cfg = cfg
            conn = sqlite3.connect(self._cfg.DB_NAME)
            self._connection_pool = list()
            self._connection_pool_in_use = list()
            self._lock = asyncio.Lock()
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
            async with self._lock:
                while not self._connection_pool:
                    await asyncio.sleep(0.01)
                conn = self._connection_pool.pop(0)
                self._connection_pool_in_use.append(conn)

            yield conn
        except BaseException as e:
            self._logger.error(e)
        finally:
            async with self._lock:
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


class DbFetcher:
    ...
