from functools import wraps
import inspect
import json
import sys
import socket
import logging
import threading
import time
from utils import load_configs, get_message, send_message
from loggers import server_log_config

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
decorated_get_message = log_decorator(get_message)
decorated_send_message = log_decorator(send_message)


@log_decorator
def handle_message(message, CONFIGS):
    if not (CONFIGS.get('ACTION') in message):
        logger.error(
            'Response message for client was created.Response code: 400')
        return {
            CONFIGS.get('RESPONSE'): 400,
            CONFIGS.get('ERROR'): 'Bad Request'
        }
    if not (CONFIGS.get('TIME') in message):
        logger.error(
            'Response message for client was created.Response code: 400')
        return {
            CONFIGS.get('RESPONSE'): 400,
            CONFIGS.get('ERROR'): 'Bad Request'
        }
    if not ((CONFIGS.get('USER') in message) or (CONFIGS.get('SENDER') in message)):
        logger.error(
            'Response message for client was created.Response code: 400')
        return {
            CONFIGS.get('RESPONSE'): 400,
            CONFIGS.get('ERROR'): 'Bad Request'
        }

    # if (CONFIGS.get('DESTINATION') in message) and (CONFIGS.get('MESSAGE_TEXT') in message):
    #     pass

    if message[CONFIGS.get('ACTION')] == CONFIGS.get('PRESENCE'):
        logger.info('Response message to client created.Response code:200')
        return {CONFIGS.get('RESPONSE'): 200, 'INIT': True}

    if message[CONFIGS.get('ACTION')] == CONFIGS.get('EXIT'):
        logger.info('Response message to client created.Response code:200')
        return {CONFIGS.get('RESPONSE'): 200, CONFIGS.get('USER'): message.get('USER')}

    if message.get('message_text'):
        logger.info(f'Recieved message from user, to another user')
        return {CONFIGS.get('RESPONSE'): 200}


@log_decorator
def client_handler(user_name, connections, responses=None):
    print(f"client handler for {user_name} was created")
    conn_semaprhore = threading.Semaphore(1)
    print('Запустился поток на клиента', user_name)
    conn_semaprhore.acquire()
    client_socket = connections.get(user_name)
    conn_semaprhore.release()
    while True:
        try:
            message = decorated_get_message(
                opened_socket=client_socket, CONFIGS=CONFIGS)
        except (ValueError, json.JSONDecodeError):
            logger.fatal('Принято некорретное сообщение от клиента')
            client_socket.close()
        except OSError:
            continue

        if message.get('action') == 'exit':
            decorated_send_message(client_socket, message, CONFIGS)

            conn_semaprhore.acquire()
            connections.pop(message.get('user'))
            conn_semaprhore.release()

            client_socket.close

        if not message.get('destination') in connections.keys():
            print("Not found destination!")
            decorated_send_message(client_socket, fail_message, CONFIGS)
        else:
            conn_semaprhore.acquire()
            destination_socket = connections.get(message.get('destination'))
            conn_semaprhore.release()
            decorated_send_message(destination_socket, message, CONFIGS)


@log_decorator
def main():
    global CONFIGS

    CONFIGS = decorated_load_configs()
    print('Сервер запущен')
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = CONFIGS.get('DEFAULT_PORT')
        if not 65535 >= listen_port >= 1024:
            raise ValueError
    except IndexError:
        logger.error('После -\'p\' необходимо указать порт')
        sys.exit(1)
    except ValueError:
        logger.error('Порт должен быть указан в пределах от 1024 до 65535')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        logger.error('После \'a\'- необходимо указать адрес для подключения')
        sys.exit(1)

    connections = dict()
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
                message = decorated_get_message(client, CONFIGS)
                response = handle_message(message, CONFIGS)
                print(response)
                print(message)
                if response.get('INIT', False):
                    connections[message.get('user')] = client
                    reciever = threading.Thread(
                        target=(client_handler), args=(message.get('user'), connections))
                    thread_list.append(reciever)
                    reciever.daemon = True
                    thread_list.append(reciever)
                    decorated_send_message(client, response, CONFIGS)
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
