import argparse
import inspect
import json
import sys
import socket
import threading
import time
import logging
from functools import wraps

from utils import load_configs, send_message, get_message

from loggers import client_log_config
from loggers import wrap_logger


CONFIGS = dict()


help_text = 'Поддерживаемые команды:\n \
message - отправить сообщение. Кому и текст будет запрошены отдельно. \n \
help - вывести подсказки по командам \n \
exit - выход из программы'


logger = logging.getLogger('client')
wrap_logger_decor = logging.getLogger('client_wrap_logger')


def log_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        object = inspect.stack()[1][3]
        cal_time_format = time.strftime("%x %X")
        func_name = func.__name__
        wrap_logger_decor.info(
            f'{cal_time_format} Функция --{func_name}-- вызвана из функции --{object}-- \n')
        return func(*args, **kwargs)
    return wrapper


decorated_load_configs = log_decorator(load_configs)
decorated_get_message = log_decorator(get_message)
decorated_send_message = log_decorator(send_message)


@log_decorator
def create_presence_message(account_name, action, CONFIGS):
    message = {
        CONFIGS.get('ACTION'): CONFIGS.get(f'{action.upper()}'),
        CONFIGS.get('TIME'): time.time(),
        CONFIGS.get('USER'): account_name
    }
    logger.info(f'created {action} message')
    return message


@log_decorator
def arg_parser(CONFIGS):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'addr', default=CONFIGS['DEFAULT_IP_ADDRESS'], nargs='?')
    parser.add_argument(
        'port', default=CONFIGS['DEFAULT_PORT'], type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        logger.critical('Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        logger.critical(
            f'Указан недопустимый режим работы {client_mode}, допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


@log_decorator
def handle_response(message, CONFIGS):
    if CONFIGS.get('RESPONSE') in message:
        if message[CONFIGS.get('RESPONSE')] == 200:
            print('200 : OK')
            logger.info(
                'Клиент подключился к серверу, получил ответ: 200 : OK')
            return
    print(f'400 : {message[CONFIGS.get("ERROR")]}')
    logger.error(f'raised ValueError in HandleResponse()')
    raise ValueError


@log_decorator
def message_from_server(sock, my_username):
    print('\n reciever запустился')
    while True:
        print('новая итерация')
        logger.info('новая итерация')
        try:
            logger.info('попытка принять сообщение от сервера')
            message = decorated_get_message(sock, CONFIGS)
            logger.info('Приянто сообщение для пользователя')
            print(
                f"Пользователь {message.get('sender')} отправил вам сообщение: {message.get('message_text')}")
        except (ValueError, json.JSONDecodeError):
            print('плохое сообщение')
            logger.fatal('Принято некорретное сообщение от клиента')
        finally:
            continue
        #     message = decorated_get_message(sock, CONFIGS)
        #     if CONFIGS['ACTION'] in message and message[CONFIGS['ACTION']] == CONFIGS['MESSAGE'] and \
        #             CONFIGS['SENDER'] in message and CONFIGS['DESTINATION'] in message \
        #             and CONFIGS['MESSAGE_TEXT'] in message and message[CONFIGS['DESTINATION']] == my_username:
        #         print(f'\nПолучено сообщение от пользователя {message[CONFIGS["SENDER"]]}:'
        #               f'\n{message[CONFIGS["MESSAGE_TEXT"]]}')
        #         logger.info(f'Получено сообщение от пользователя {message[CONFIGS["SENDER"]]}:'
        #                     f'\n{message[CONFIGS["MESSAGE_TEXT"]]}')
        #     else:
        #         logger.error(
        #             f'Получено некорректное сообщение с сервера: {message}')
        # except (OSError, ConnectionError, ConnectionAbortedError,
        #         ConnectionResetError, json.JSONDecodeError):
        #     logger.critical(f'Потеряно соединение с сервером.')
        #     break


@log_decorator
def create_exit_message(account_name):
    return {
        CONFIGS['ACTION']: CONFIGS['EXIT'],
        CONFIGS['TIME']: time.time(),
        CONFIGS['ACCOUNT_NAME']: account_name
    }


@log_decorator
def create_message(sock, account_name):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        CONFIGS['ACTION']: CONFIGS['MESSAGE'],
        CONFIGS['SENDER']: account_name,
        CONFIGS['DESTINATION']: to_user,
        CONFIGS['TIME']: time.time(),
        CONFIGS['MESSAGE_TEXT']: message
    }
    logger.info(f'Сформирован словарь сообщения: {message_dict}')
    try:
        decorated_send_message(sock, message_dict, CONFIGS)
        logger.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        logger.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log_decorator
def user_interface_graphics(sock, my_username):
    print(help_text)
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, my_username)
        elif command == 'help':
            print(help_text)
        elif command == 'exit':
            decorated_send_message(
                sock, create_exit_message(my_username), CONFIGS)
            print('Завершение соединения.')
            logger.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print(
                'Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


def main():
    global CONFIGS

    CONFIGS = decorated_load_configs(is_server=False)
    thread_list = []
    server_address, server_port, client_mode = arg_parser(CONFIGS)
    client_name = input("введите имя пользователя \n")

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))

        decorated_send_message(transport, create_presence_message(
            CONFIGS=CONFIGS, action='presence', account_name=client_name), CONFIGS)
        answer = handle_response(
            decorated_get_message(transport, CONFIGS), CONFIGS)
        logger.info(
            f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
        connected = True
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)

    if connected:
        receiver = threading.Thread(
            target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface_graphics(transport, client_name)

#       прогуглить трединг и поменять на .run()
#       прогуглить трединг и поменять на .run()
        logger.debug('Запущены процессы')


if __name__ == '__main__':
    main()
