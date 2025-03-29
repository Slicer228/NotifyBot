from logging.handlers import RotatingFileHandler
import logging


class Logger(logging.Logger):

    def __init__(self):
        super().__init__('prod', logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
        file_handler = RotatingFileHandler(
            'logs.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=1,
            encoding='utf-8',
        )
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)
