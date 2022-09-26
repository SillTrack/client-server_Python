import logging
import sys

from logging.handlers import TimedRotatingFileHandler
from time import sleep
import os




formatter = logging.Formatter("%(asctime)s - %(levelname)8s - %(module)s - %(message)s ")

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

logger = logging.getLogger('client')
file_handler = logging.FileHandler("log//client.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def console_add():
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    return console

if __name__ == '__main__':
    # console = console_add()
    # logger.addHandler(console)
    logger.info('Тестовый запуск логирования')


