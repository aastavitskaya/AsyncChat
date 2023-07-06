import os
import sys

sys.path.append(os.getcwd())

from log import LoggerProxy

proxy = LoggerProxy("client")
logger = proxy.get_logger()


if __name__ == "__main__":
    logger.critical("Critical error")
    logger.error("Error")
    logger.debug("Debug information")
    logger.info("Information")
