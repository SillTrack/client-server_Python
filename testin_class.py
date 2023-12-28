from functools import wraps
import inspect
import time


class CallBack():
    def __init__(self):
        pass


    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            object = inspect.stack()[1][3]
            cal_time_format = time.strftime("%x %X")
            func_name = func.__name__
            print(cal_time_format, "Имя вызывающего объекта:",
            object, "\n", f"Имя вызванного объекта: {func_name}")
            return 0
        return decorated



@CallBack() 
def primitive_func(number):
    print(f'{number*number}')



def main():
    primitive_func(2)


if __name__ == '__main__':
    main()