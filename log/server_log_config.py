
import logging
from logging.handlers import TimedRotatingFileHandler

import time

logging_level = 20
log_file_name = 'server.log'

formatter = logging.Formatter("%(asctime)s - %(levelname)8s - %(module)s - %(message)s ")



rotation_logging_handler = TimedRotatingFileHandler(filename='log//server.log',when='D', interval=1, backupCount=5,encoding='utf=8')
rotation_logging_handler.suffix = '%Y-%m-%d'
rotation_logging_handler.setLevel(logging.INFO)
rotation_logging_handler.setFormatter(formatter)

logger = logging.getLogger('server')


logger.addHandler(rotation_logging_handler)
logger.setLevel(logging.INFO)


try:
    for i in range(50):
        time.sleep(0.1)
        logger.debug('i=%d' % i)
        logger.info('i=%d' % i)
        logger.warning('i=%d' % i)
        logger.error('i=%d' % i)
        logger.critical('i=%d' % i)
except KeyboardInterrupt:
    # handle Ctrl-C
    logging.warn("Cancelled by user")
except Exception as ex:
    # handle unexpected script errors
    logging.exception("Unhandled error\n{}".format(ex))
    raise
finally:
    # perform an orderly shutdown by flushing and closing all handlers; called at application exit and no further use of the logging system should be made after this call.
    logging.shutdown()
    rotation_logging_handler.doRollover()