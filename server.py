from cmath import log
import json
import sys
import socket
import logging

from utils import load_configs, get_message, send_message


CONFIGS = dict()

logger = logging.getLogger('server')


def handle_message(message, CONFIGS):
    if CONFIGS.get('ACTION') in message \
            and (message[CONFIGS.get('ACTION')] == CONFIGS.get('PRESENCE')
                 or message[CONFIGS.get('ACTION')] == CONFIGS.get('EXIT')) \
            and CONFIGS.get('TIME') in message \
            and CONFIGS.get('USER') in message \
            and message[CONFIGS.get('USER')][CONFIGS.get('ACCOUNT_NAME')] == 'Guest':
        logger.info('Response message to client created.Response code:200')
        return {CONFIGS.get('RESPONSE'): 200}
    logger.error('Response message for client was created.Response code: 400')
    return {
        CONFIGS.get('RESPONSE'): 400,
        CONFIGS.get('ERROR'): 'Bad Request'
    }


def main():
    global CONFIGS
    CONFIGS = load_configs()
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

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(CONFIGS.get('MAX_CONNECTIONS'))
    client, client_address = transport.accept()
    message = get_message(client, CONFIGS)
    while message.get('action') != 'exit':
        try:
            response = handle_message(message, CONFIGS)
            print(response)
            print(message)
            send_message(client, response, CONFIGS)
            message = get_message(client, CONFIGS)
            logger.info('Сервер принял сообщение от клиента')
        except (ValueError, json.JSONDecodeError):
            logger.fatal('Принято некорретное сообщение от клиента')
            client.close()
    response = handle_message(message, CONFIGS)
    print(response)
    print(message)
    send_message(client, response, CONFIGS)
    client.close()


if __name__ == '__main__':
    main()
