import unittest
from unittest.mock import MagicMock

import ctypes
import tslib_so_interface as tslib

buffer_return_value = "test buffer return value"


def string_buff_side_effect(self, tuple_name, string_buffer, string_buffer_size):
    string_buffer = ctypes.create_string_buffer(100)
    string_buffer.value = "test value"
    return 100


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
        MagicMock.side_effect = string_buff_side_effect
        return_value = tslib.tsread(tp_name, string_buff_size)
        self.assertEqual(return_value, buffer_return_value)
        tslib.libso.tsread.assert_called_with(tp_name, string_buff_size)

    def test_tsread_failure(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsread = MagicMock()
        MagicMock.return_value = 101
        MagicMock.side_effect = string_buff_side_effect
        return_value = tslib.tsread(tp_name, string_buff_size)
        self.assertEqual(return_value, 1)
        tslib.libso.tsread.assert_called_with(tp_name, string_buff_size)


if __name__ == '__main__':
    unittest.main()

