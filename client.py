import argparse
import inspect
import json
import sys
import socket
import threading
import time
import logging
from functools import wraps
import os

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from utils import load_configs

from utils import BaseChatFuncs

from loggers import client_log_config
from loggers import wrap_logger

from db_client_creating import ClientDataBase, MessageHistory, ContactList


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


decorated_load_configs = log_decorator(
    load_configs)


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


class MesaagerClient(BaseChatFuncs):

    def __init__(self, account_name: str, CONFIGS):
        super().__init__(CONFIGS)
        self.account_name = account_name

    def Add_Contact(self, action, contact, db_engine):

        message = {
            CONFIGS.get('ACTION'): self.configs.get(f'{action.upper()}'),
            CONFIGS.get('USER_ID'): contact,
            CONFIGS.get('TIME'): time.time(),
            CONFIGS.get('USER'): self.account_name
        }
        with Session(db_engine) as session:
            new_contact = ContactList(contact_name=contact)
            session.add(new_contact)
            session.commit()
            session.close()

        logger.info(f'created {action} message')
        return message

    def Delete_Contact(self, action, contact, db_engine):

        message = {
            CONFIGS.get('ACTION'): self.configs.get(f'{action.upper()}'),
            CONFIGS.get('USER_ID'): contact,
            CONFIGS.get('TIME'): time.time(),
            CONFIGS.get('USER'): self.account_name
        }
        with Session(db_engine) as session:
            contact_to_delete = session.query(
                ContactList).filter_by(contact_name=contact).first()
            if contact_to_delete:
                session.delete(contact_to_delete)
                session.commit()
            else:
                print("Запись не найдена")

            session.close()
        logger.info(f'created {action} message')
        return message

    @log_decorator
    def get_message(self, opened_socket):
        return super().get_message(opened_socket)

    @log_decorator
    def send_message(self, opened_socket, message):
        return super().send_message(opened_socket, message)

    @log_decorator
    def create_function_message(self, action, db_engine):
        message = {
            CONFIGS.get('ACTION'): self.configs.get(f'{action.upper()}'),
            CONFIGS.get('TIME'): time.time(),
            CONFIGS.get('USER'): self.account_name
        }

        logger.info(f'created {action} message')
        return message

    @log_decorator
    def handle_response(self, message):
        if self.configs.get('RESPONSE') in message:
            if message[self.configs.get('RESPONSE')] == 200:
                print('200 : OK')
                logger.info(
                    'Клиент подключился к серверу, получил ответ: 200 : OK')
                return
        print(f'400 : {message[self.configs.get("ERROR")]}')
        logger.error(f'raised ValueError in HandleResponse()')
        raise ValueError

    @log_decorator
    def message_from_server(self, sock):
        print('\n reciever запустился')
        while True:
            print('новая итерация')
            logger.info('новая итерация')
            try:
                logger.info('попытка принять сообщение от сервера')
                message = self.get_message(sock)
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
    def create_exit_message(self):
        return {
            self.configs['ACTION']: self.configs['EXIT'],
            self.configs['TIME']: time.time(),
            self.configs['ACCOUNT_NAME']: self.account_name
        }

    @log_decorator
    def create_message(self, sock, db_engine):
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            self.configs['ACTION']: self.configs['MESSAGE'],
            self.configs['SENDER']: self.account_name,
            self.configs['DESTINATION']: to_user,
            self.configs['TIME']: time.time(),
            self.configs['MESSAGE_TEXT']: message
        }
        logger.info(f'Сформирован словарь сообщения: {message_dict}')
        try:
            self.send_message(sock, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {to_user}')
            with Session(db_engine) as session:
                message = MessageHistory(
                    receiver=to_user, message_text=message)
                session.add(message)
                session.commit()
                session.close()
        except:
            logger.critical('Потеряно соединение c сервером.')
            sys.exit(1)

    @log_decorator
    def user_interface_graphics(self, sock, db_engine):
        print(help_text)
        while True:
            command = input('Введите команду: ')

            if command == 'message':

                self.create_message(sock, db_engine=db_engine)
            elif command == 'help':
                print(help_text)

            elif command == 'get_contacts':
                self.send_message(self.create_function_message(action=command))

            elif command == 'add_contacts':

                name = input('Введите имя контакта')
                self.send_message(self.Add_Contact(
                    action='add_contacts', contact=name, db_engine=db_engine))

            elif command == 'delete_contacts':

                name = input('Введите имя контакта')
                self.send_message(self.Delete_Contact(
                    action='delete_contacts', contact=name, db_engine=db_engine))

            elif command == 'exit':
                self.send_message(
                    sock, self.create_exit_message())
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print(
                    'Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


CONFIGS = dict()

Base = declarative_base()

help_text = 'Поддерживаемые команды:\n \
message - отправить сообщение. Кому и текст будет запрошены отдельно. \n \
add_contact - добавить пользователя в список контактов. \n \
delete_contact - удалить пользователя из списка контактов. \n \
help - вывести подсказки по командам \n \
exit - выход из программы'


# decorated_get_message = log_decorator(get_message)  # перевел в клиента из utils
# decorated_send_message = log_decorator(send_message) # перевел в клиента из utils


def main():
    global CONFIGS

    CONFIGS = decorated_load_configs(is_server=False)
    # thread_list = []

    server_address, server_port, client_mode = arg_parser(CONFIGS)

    client_name = input("введите имя пользователя \n")

    db_engine = create_engine("sqlite:///client_tables.db", echo=True)
    db_prototype = ClientDataBase(engine=db_engine, base=Base)
    print(db_prototype.create_db())

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))

        client = MesaagerClient(client_name, CONFIGS)

        presence_message = client.create_function_message(
            action='presence')

        client.send_message(transport, presence_message)

        answer = client.handle_response(
            client.get_message(transport))
        logger.info(
            f'Установлено соединение c сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение c сервером.')
        connected = True
    except json.JSONDecodeError:
        logger.error('He удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(
            f'He удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)

    if connected:
        receiver = threading.Thread(
            # target=client.message_from_server, args=(transport)) # ругается что аргумент - сокет а не iterable
            target=client.message_from_server, args=([transport]))
        receiver.daemon = True
        receiver.start()

        client.user_interface_graphics(transport, db_engine=db_engine)

#       прогуглить трединг и поменять на .run()
#       прогуглить трединг и поменять на .run()
        logger.debug('Запущены процессы')


if __name__ == '__main__':
    main()
