
import select
from socket import socket, AF_INET, SOCK_STREAM
from tabnanny import check


def status_check(client_sock):
    try:
        status_flag = client_sock.recv(1024).decode('utf-8')
    except:
        print('Клиент {}, {} отключился'.format(
            client_sock.fileno(), client_sock.getpeername()))
        return
    finally:
        if status_flag == "w":
            return True
    return


def read_requsets(r_clients, all_clients):
    responses = {}

    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            responses[sock] = data
        except:
            print('Клиент {}, {} отключился'.format(
                sock.fileno(), sock.getpeername()))
            all_clients.remove(sock)

    return responses


def write_responses(requests, w_clients, all_clients):
    for sock in w_clients:
        if requests.get(sock) != None:
            try:
                resp = requests.get(sock).encode('utf-8')
                for sock_to_send in all_clients:
                    try:
                        sock_to_send.send(resp.upper())
                    except:
                        print('Клиент {}, {} отключился'.format(
                            sock.fileno(), sock.getpeername()))
                        sock.close()
                        all_clients.remove(sock)
            except:
                print('Клиент {}, {} отключился'.format(
                    sock.fileno(), sock.getpeername()))
                sock.close()
                all_clients.remove(sock)


def mainloop():
    address = ('', 8888)
    all_clients = []
    read_clients = []
    check_read = True

    s = socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(5)
    s.settimeout(0.2)
    while True:
        try:
            conn, addr = s.accept()
        except OSError as e:
            pass
        else:
            print("получен запрос на соединение от %s" % str(addr))
            check_read = False
            all_clients.append(conn)
        finally:
            wait = 0
            r = []
            w = []
            if check_read == False:
                read_required = status_check(conn)
                if read_required == True:
                    read_clients.append(conn)
                check_read = True

            try:
                # read_clients
                r, w, e = select.select(read_clients, all_clients, [], wait)
            except:
                pass
            requests = read_requsets(r, all_clients)
            write_responses(requests, w, all_clients)


if __name__ == '__main__':
    print('эхо сервер запущен')
    mainloop()
