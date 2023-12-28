
from functools import wraps
import inspect
import json
import os
import sys
import time


def load_configs(is_server=True):
    config_keys = [
        'DEFAULT_PORT',
        'MAX_CONNECTIONS',
        'MAX_PACKAGE_LENGTH',
        'ENCODING',
        'ACTION',
        'TIME',
        'USER',
        'ACCOUNT_NAME',
        'PRESENCE',
        'RESPONSE',
        'ERROR'
    ]
    if not is_server:
        config_keys.append('DEFAULT_IP_ADDRESS')
    if not os.path.exists('config.json'):
        print('Файл конфигурации не найден')
        sys.exit(1)
    with open('config.json') as config_file:
        CONFIGS = json.load(config_file)
    loaded_configs_keys = list(CONFIGS.keys())
    for key in config_keys:
        if key not in loaded_configs_keys:
            print(f'В файле конфигурации не хватает ключа: {key}')
            sys.exit(1)
    return CONFIGS


class BaseChatFuncs:

    def __init__(self, CONFIGS):
        self.configs = CONFIGS

    def send_message(self, opened_socket, message):
        json_message = json.dumps(message)
        response = json_message.encode(self.configs.get('ENCODING'))
        opened_socket.send(response)

    def get_message(self, opened_socket):
        response = opened_socket.recv(self.configs.get('MAX_PACKAGE_LENGTH'))
        if isinstance(response, bytes):
            json_response = response.decode(self.configs.get('ENCODING'))
            response_dict = json.loads(json_response)
            if isinstance(response_dict, dict):
                return response_dict
            raise ValueError
        raise ValueError


# def log_decorator(func):

#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         object = inspect.stack()[1][3]
#         cal_time_format = time.strftime("%x %X")
#         func_name = func.__name__
#         debug_log.write(cal_time_format + f"Функция {func_name} вызвана из функции {object}" + "\n")
#         return func(*args, **kwargs)
#     return wrapper
