import dotenv
from src.logger import Logger


class Config:
    __slots__ = ('_logger', '_env_vals')

    def __init__(self, logger: Logger):
        # pay attention to launch project via "main.py" script, for correct path tracing
        try:
            self._logger = logger
            self._env_vals = dotenv.dotenv_values()
        except FileNotFoundError:
            self._logger.critical('Could not find .env file')

    def __getattr__(self, item: str):
        return self._env_vals[item]


