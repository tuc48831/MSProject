import unittest
import ctypes
from unittest.mock import MagicMock

import tslib_so_interface as tslib


class MyTestCase(unittest.TestCase):

    def test_tsput_success(self):
        tp_name = "testTuple"
        tp_value = "This is the tuple value"
        tp_size = 100
        tslib.libso.tsput = MagicMock()
        MagicMock.return_value = 100
        return_value = tslib.tsput(tp_name, tp_value, tp_size)
        self.assertEqual(return_value, 0)
        tslib.libso.tsput.assert_called_with(tp_name, tp_value, tp_size)

    def test_tsput_failure(self):
        tp_name = "testTuple"
        tp_value = "This is the tuple value"
        tp_size = 100
        tslib.libso.tsput = MagicMock()
        # think this is the 'real' tsput err code
        MagicMock.return_value = -104
        return_value = tslib.tsput(tp_name, tp_value, tp_size)
        self.assertEqual(return_value, 1)
        tslib.libso.tsput.assert_called_with(tp_name, tp_value, tp_size)

    def test_tsread_success(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsread = MagicMock()
        MagicMock.return_value = 100
        return_value = tslib.tsread(tp_name, string_buff_size)
        self.assertEqual(return_value, (b'', b'testTuple'))

    def test_tsread_failure(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsread = MagicMock()
        MagicMock.return_value = -108
        return_value = tslib.tsread(tp_name, string_buff_size)
        self.assertEqual(return_value, 1)

    def test_tsget_success(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsget = MagicMock()
        MagicMock.return_value = 100
        return_value = tslib.tsget(tp_name, string_buff_size)
        self.assertEqual(return_value, (b'', b'testTuple'))

    def test_tsget_failure(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsget = MagicMock()
        MagicMock.return_value = -107
        return_value = tslib.tsget(tp_name, string_buff_size)
        self.assertEqual(return_value, 1)


if __name__ == '__main__':
    unittest.main()

