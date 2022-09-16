import unittest
import socket
import json
import time 

from utils import get_message, load_configs, send_message

from client import CONFIGS, create_presence_message, handle_response

# во время тестов должен быть включен сервер 

class CreatePresenceMessageTest(unittest.TestCase):

    def setUp(self) -> None:
        self.confings = load_configs(is_server=False)
        self.presence_message_action_presence = 'presence'
        self.presence_message_action_exit = 'exit'
        
    def check_presence_message_action_presence(self):
        self.check_presence_message_type()
        message = create_presence_message('guest', 'presence', self.confings)
        self.assertEqual(message.get('action'), self.presence_message_action_presence)
    
    {'action': 'presence', 'time': 1663166600.9883285, 'user': {'account_name': 'Guest'}}

    def check_presence_message_action_exit(self):
        self.check_presence_message_type()
        message = create_presence_message('guest', 'exit', self.confings)
        self.assertEqual(message.get('action'), self.presence_message_action_exit)

    def check_presence_message_type(self):
        message = create_presence_message('guest', 'presence', self.confings)
        self.assertEqual(type(message), list)


    def tearDown(self) -> None:
        pass


class HandleResponseTest(unittest.TestCase):

    def setUp(self) -> None:
        self.response_200 = '200 : OK'
        self.response_400 = '400 : error'
        self.confings = load_configs(is_server=False)
        self.test_message = create_presence_message('guest', 'presence', self.confings)

        
    def test_handle_200(self):
        test_response = handle_response({'response': 200}, self.confings)
        self.assertEqual(test_response, self.response_200)

    def test_handle_400(self):
        test_response = handle_response({'response': 400}, self.confings)
        self.assertEqual(test_response, self.response_400)

class GetMessageTest(unittest.TestCase):

    def setUp(self) -> None:
        self.response_message = {'response': 200}

    def test_get_message_type(self):
        CONFIGS = load_configs(is_server=False)
        server_address = CONFIGS.get('DEFAULT_IP_ADDRESS')
        server_port = CONFIGS.get('DEFAULT_PORT')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        presence_message = create_presence_message('Guest', 'presence', CONFIGS)
        send_message(transport, presence_message, CONFIGS)
        response = get_message(transport, CONFIGS)
        self.assertEqual(type(response), dict)
    
    def test_get_message_content(self):
        CONFIGS = load_configs(is_server=False)
        server_address = CONFIGS.get('DEFAULT_IP_ADDRESS')
        server_port = CONFIGS.get('DEFAULT_PORT')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        presence_message = create_presence_message('Guest', 'presence', CONFIGS)
        send_message(transport, presence_message, CONFIGS)
        response = get_message(transport, CONFIGS)
        self.assertEqual(response, self.response_message)

if __name__ == '__main__':
    unittest.main()