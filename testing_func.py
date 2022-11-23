import time
import inspect
from functools import wraps

def log(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        object = inspect.stack()[1][3]
        cal_time_format = time.strftime("%x %X")
        func_name = func.__name__
        print(cal_time_format, "Имя вызывающего объекта:",
          object, "\n", f"Имя вызванного объекта: {func_name}")
        return func(*args, **kwargs)

    return wrapper


@log
def primitive_func(number):
    print(f'{number*number}')


def main():
    primitive_func(2)


if __name__ == '__main__':
    main()
