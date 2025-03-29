

if __name__ == "__main__":
    from src.config import Config
    from src.logger import Logger
    from src.db import DbInteractor

    logger = Logger()
    cfg = Config(logger)
    try:
        db = DbInteractor(logger, cfg)
    finally:
        db.close_all_connections()



