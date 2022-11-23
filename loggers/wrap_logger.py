from functools import wraps
import inspect
import logging
from logging.handlers import TimedRotatingFileHandler
import time



wrap_formatter = logging.Formatter(
    " %(message)s ")

wrap_handler = logging.FileHandler(filename='loggers//client_calls.log', mode='w', encoding='utf-8' ) 

wrap_handler.setLevel(logging.INFO)
wrap_handler.setFormatter(wrap_formatter)

wrap_log = logging.getLogger('client_wrap_logger')


wrap_log.addHandler(wrap_handler)
wrap_log.setLevel(logging.INFO)

def log_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        object = inspect.stack()[1][3]
        cal_time_format = time.strftime("%x %X")
        func_name = func.__name__
        wrap_log.info(
            f'{cal_time_format} Функция --{func_name}-- вызвана из функции --{object}-- \n')
        return func(*args, **kwargs)
    return wrapper




@log_decorator
def bin_func(number):
    binary_list = []
    while number > 1:
        temporary = number % 2
        binary_list.append(temporary)
        number /= 2
        number = int(number)
    binary_list.append(1)
    binary_list.reverse()
    print(binary_list)
    return binary_list


def main():
    number_to_binary = int(input('Введите число\n'))
    bin_number_to_binary = bin_func(number_to_binary)


if __name__ == '__main__':
    main()