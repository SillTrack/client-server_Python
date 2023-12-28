
import logging


wrap_formatter = logging.Formatter(
    "%(asctime)s - %(message)s ")

wrap_handler = logging.FileHandler(filename='loggers//server.log', mode='w', encoding='utf-8' ) 

wrap_handler.setLevel(logging.INFO)
wrap_handler.setFormatter(wrap_formatter)

wrap_logger = logging.getLogger('server_wrap_logger')


wrap_logger.addHandler(wrap_handler)
wrap_logger.setLevel(logging.INFO)

