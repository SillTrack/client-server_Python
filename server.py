from functools import wraps
import inspect
import json
import sys
import socket
import logging
import threading
import time
import os
from utils import load_configs
from loggers import server_log_config
from utils import BaseChatFuncs
from db_server_creating import Server_DataBase
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()

CONFIGS = dict()
fail_message = {
    CONFIGS.get('ACTION'): CONFIGS.get("Fail"),
    CONFIGS.get('TIME'): time.time(),
    CONFIGS.get('MESSAGE'): 'failed to send message'
}

logger = logging.getLogger('server')
wrap_log = logging.getLogger('server_wrap_logger')


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


decorated_load_configs = log_decorator(load_configs)


class MessangerServer(BaseChatFuncs):

    def __init__(self, CONFIGS):
        super().__init__(CONFIGS)
        db_engine = create_engine("sqlite:///server_tables.db", echo=True)
        self.database = Server_DataBase(engine=db_engine, base=Base)

    @log_decorator
    def handle_message(self, message):
        if not (self.configs.get('ACTION') in message):
            logger.error(
                'Response message for client was created.Response code: 400')
            return {
                self.configs.get('RESPONSE'): 400,
                self.configs.get('ERROR'): 'Bad Request'
            }
        if not (self.configs.get('TIME') in message):
            logger.error(
                'Response message for client was created.Response code: 400')
            return {
                self.configs.get('RESPONSE'): 400,
                self.configs.get('ERROR'): 'Bad Request'
            }
        if not ((self.configs.get('USER') in message) or (self.configs.get('SENDER') in message)):
            logger.error(
                'Response message for client was created.Response code: 400')
            return {
                self.configs.get('RESPONSE'): 400,
                self.configs.get('ERROR'): 'Bad Request'
            }

        # if (CONFIGS.get('DESTINATION') in message) and (CONFIGS.get('MESSAGE_TEXT') in message):
        #     pass

        if message[self.configs.get('ACTION')] == self.configs.get('PRESENCE'):
            logger.info('Response message to client created.Response code:200')
            return {self.configs.get('RESPONSE'): 200, 'INIT': True}

        if message[self.configs.get('ACTION')] == self.configs.get('EXIT'):
            logger.info('Response message to client created.Response code:200')
            return {self.configs.get('RESPONSE'): 200, self.configs.get('USER'): message.get('USER')}

        if message[self.configs.get('ACTION') == self.configs.get('GET_CONTACTS')]:
            pass

        if message[self.configs.get('ACTION') == self.configs.get('ADD_CONTACT')]:
            pass

        if message[self.configs.get('ACTION') == self.configs.get('DELETE_CONTACT')]:
            pass

        if message.get('message_text'):
            logger.info(f'Recieved message from user, to another user')
            return {self.configs.get('RESPONSE'): 200}

    @log_decorator
    def client_handler(self, user_name, connections, responses=None):
        print(f"client handler for {user_name} was created")
        conn_semaprhore = threading.Semaphore(1)
        print('Запустился поток на клиента', user_name)
        conn_semaprhore.acquire()
        client_socket = connections.get(user_name)
        conn_semaprhore.release()
        while True:
            try:
                message = self.get_message(
                    opened_socket=client_socket)
            except (ValueError, json.JSONDecodeError):
                logger.fatal('Принято некорретное сообщение от клиента')
                client_socket.close()
            except OSError:
                continue

            if message.get('action') == 'exit':
                self.send_message(client_socket, message)

                conn_semaprhore.acquire()
                connections.pop(message.get('user'))
                conn_semaprhore.release()

                client_socket.close

            if not message.get('destination') in connections.keys():
                print("Not found destination!")
                self.send_message(client_socket, fail_message)
            else:
                conn_semaprhore.acquire()
                destination_socket = connections.get(
                    message.get('destination'))
                conn_semaprhore.release()
                self.send_message(destination_socket, message)


def main():

    CONFIGS = decorated_load_configs()

    server = MessangerServer(CONFIGS)

    print('Сервер запущен')

    print(server.database.create_db())

    # try:
    #     if '-p' in sys.argv:
    #         listen_port = int(sys.argv[sys.argv.index('-p') + 1])
    #     else:
    #         listen_port = CONFIGS.get('DEFAULT_PORT')
    #     if not 65535 >= listen_port >= 1024:
    #         raise ValueError
    # except IndexError:
    #     logger.error('После -\'p\' необходимо указать порт')
    #     sys.exit(1)
    # except ValueError:
    #     logger.error('Порт должен быть указан в пределах от 1024 до 65535')
    #     sys.exit(1)

    # try:
    #     if '-a' in sys.argv:
    #         listen_address = sys.argv[sys.argv.index('-a') + 1]
    #     else:
    #         listen_address = ''

    # except IndexError:
    #     logger.error('После \'a\'- необходимо указать адрес для подключения')
    #     sys.exit(1)

    connections = dict()
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    listen_address = ""
    listen_port = 7777
    transport.bind((listen_address, listen_port))

    transport.listen(CONFIGS.get('MAX_CONNECTIONS'))
    transport.settimeout(0.5)
    thread_list = []
    # Все взаимодействия с connections (Добавление удаление) через семафоры,mutex

    while True:
        time.sleep(2)
        print('сервер ждет следующего клиента')
        client = None
        try:
            client, address = transport.accept()
            print('к серверу подключился новый клиент')
        except OSError as e:
            pass

        try:
            if not client == None:
                message = server.get_message(client)
                response = server.handle_message(message)
                print(response)
                print(message)
                if response.get('INIT', False):
                    connections[message.get('user')] = client
                    reciever = threading.Thread(
                        target=(server.client_handler), args=(message.get('user'), connections))
                    thread_list.append(reciever)
                    reciever.daemon = True
                    thread_list.append(reciever)
                    server.send_message(client, response)
                    reciever.start()

        except (ValueError, json.JSONDecodeError):
            logger.fatal('Принято некорретное сообщение от клиента')
            client.close()
        except UnboundLocalError:
            continue
        except OSError:
            continue

        # response = handle_message(message, CONFIGS)
        # print(response)
        # print(message)
        # decorated_send_message(client, response, CONFIGS)
        # client.close()


if __name__ == '__main__':
    main()
