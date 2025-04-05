import sys

if __name__ == "__main__":
    from src.config import Config
    from src.logger import Logger
    from src.db import DbFetcher

    logger = Logger()
    cfg = Config(logger)
    try:
        db = DbFetcher(logger, cfg)
    finally:
        try:
            db.close_all_connections()
        except:
            sys.exit(1)



