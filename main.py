if __name__ == "__main__":
    import sys
    from src.routers.bot import Bot
    from src.task_manager import UserTaskerFarm
    from src.config import Config
    from src.logger import Logger
    from src.db import DbFetcher

    logger = Logger()
    cfg = Config(logger)
    try:
        db = DbFetcher(logger, cfg)
        tasker = UserTaskerFarm(logger, db)
        bot = Bot(db, logger, tasker, cfg)
        bot.run()
    finally:
        try:
            db.close_all_connections()
        except:
            sys.exit(1)



