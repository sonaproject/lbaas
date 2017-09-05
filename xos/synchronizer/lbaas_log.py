import inspect

from xos.logger import Logger, logging
from os.path import basename

logger = Logger(level=logging.INFO)

def debug(msg):
    logger.debug(
                basename(str(inspect.stack()[1][1])) + ':' + 
                str(inspect.stack()[1][2]) + ' ' + 
                str(inspect.stack()[1][3]) + '()  ' + 
                str(msg))

def info(msg):
    logger.info(
                basename(str(inspect.stack()[1][1])) + ':' + 
                str(inspect.stack()[1][2]) + ' ' + 
                str(inspect.stack()[1][3]) + '()  ' + 
                str(msg))

def error(msg):
    logger.error(
                basename(str(inspect.stack()[1][1])) + ':' + 
                str(inspect.stack()[1][2]) + ' ' + 
                str(inspect.stack()[1][3]) + '()  ' + 
                str(msg))

