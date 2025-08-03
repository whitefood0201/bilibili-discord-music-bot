import logging
import logging.handlers
import time
import os
 
def setupLogger(moduleName):
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    logger = logging.getLogger(moduleName)
    logger.setLevel(logging.INFO)

    strTime = time.strftime("%Y-%m-%d", time.localtime())

    handler = logging.handlers.RotatingFileHandler(
        filename= f'./logs/discord_{strTime}.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger