from calendar import c
import unittest

from utils import load_configs


class LoadConfigsTest(unittest.TestCase):

    def setUp(self) -> None:
        self.Configs = load_configs()

    def test_return_file(self):
        self.test_file_not_blank()
        self.assertEqual(type(self.Configs), dict)

    def test_file_not_blank(self):
        self.assertNotEqual(self.Configs, None)

    def tearDown(self) -> None:
        pass

if __name__ == '__main__':
    unittest.main()