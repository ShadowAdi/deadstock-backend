import logging
import sys

def setup_logger():
    logger=logging.getLogger("DeadStock-logger")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    )
    
    console_handler=logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    return logger

logger=setup_logger()