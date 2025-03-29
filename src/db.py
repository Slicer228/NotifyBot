import asyncio
import sys
import aiosqlite
from src.logger import Logger
from src.config import Config


class DbInteractor:
    __slots__ = ('_connection_pool', '_connection_pool_in_use', '_logger', '_cfg', '_lock')

    def __init__(self, logger: Logger, cfg: Config):
        try:
            self._connection_pool = list()
            self._connection_pool_in_use = list()
            self._logger = logger
            self._cfg = cfg
            self._lock = asyncio.Lock()
            for _ in range(int(self._cfg.DB_CONN_POOL_LIMIT)):
                self._connection_pool.append(aiosqlite.connect(self._cfg.DB_NAME))
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
        for conn in self._connection_pool + self._connection_pool_in_use:
            conn.close()


class DbFetcher:
    ...
