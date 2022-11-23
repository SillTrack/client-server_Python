import unittest
import socket
import json

from utils import load_configs, get_message, send_message

from server import handle_message

# во время тестирования сервера необходимо выполнить программу клиента,
# причем в клиента придет ошиюка декодирования, так как мы не отсылаем сообщение обратно

class Test(unittest.TestCase):

    def setUp(self) -> None:
        self.configs = load_configs(is_server=False)
        self.message = 'response: 200'

    def test_handle_message_type(self):
        listen_address = self.configs.get("DEFAULT_IP_ADDRESS")
        listen_port = self.configs.get('DEFAULT_PORT')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))

        transport.listen(self.configs.get('MAX_CONNECTIONS'))
        client, client_address = transport.accept()
        message = get_message(client, self.configs)
        print(message.get('action'))
        response = handle_message(message, self.configs)
        self.assertEqual(type(response), dict)
        client.close()

# второй тест лучше выполнить в отдельном файле в связи со структурой клиентсерверных взаимодействий
 

    # def test_handle_message_content(self):
    #     listen_address = self.configs.get("DEFAULT_IP_ADDRESS")
    #     listen_port = self.configs.get('DEFAULT_PORT')
    #     transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     transport.bind((listen_address, listen_port))

    #     transport.listen(self.configs.get('MAX_CONNECTIONS'))
    #     client, client_address = transport.accept()
    #     message = get_message(client, self.configs)
    #     print(message.get('action'))
    #     response = handle_message(message, self.configs)
    #     self.assertEqual(type(response), dict)
    #     client.close()        
    #     self.assertEqual(response, self.message)

if __name__ == '__main__':
    unittest.main()