
from socket import *


ADDRESS = ('localhost', 8888)


def echo_client():
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect(ADDRESS)

        flag = input(
            'Введите флаг взаимодействия с сервером: \n r - только прослушивание сообщений \n w - только отправка сообщений \n')

        if flag == 'w':

            sock.send(flag.encode('utf-8'))
            print('Выбран режим чтения и простомтра сообщений')

        else:

            sock.send(flag.encode('utf-8'))
            print('Выбран режим только прослушивание сообщений')

        while True:

            if flag == 'w':
                msg = input("Ваше сообщение: ")

                if msg == 'exit':
                    break

                sock.send(msg.encode('utf-8'))
                data = sock.recv(1024).decode('utf-8')
                print("ответ:", data)

            else:

                data = sock.recv(1024).decode('utf-8')
                print("Другой клиент отправил на сервер:", data.lower())


if __name__ == "__main__":
    echo_client()
