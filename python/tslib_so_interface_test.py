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
        tp_name_called_with = ctypes.create_string_buffer(2*len(tp_name))
        tp_name_called_with.value = tp_name.encode('utf-8')
        string_buffer_called_with = ctypes.create_string_buffer(string_buff_size)
        tslib.libso.tsread.assert_called_with(tp_name_called_with, string_buffer_called_with, string_buff_size)

    def test_tsread_failure(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsread = MagicMock()
        MagicMock.return_value = 101
        return_value = tslib.tsread(tp_name, string_buff_size)
        self.assertEqual(return_value, 1)
        tp_name_called_with = ctypes.create_string_buffer(2*len(tp_name))
        tp_name_called_with.value = tp_name.encode('utf-8')
        string_buffer_called_with = ctypes.create_string_buffer(string_buff_size)
        tslib.libso.tsread.assert_called_with(tp_name_called_with, string_buffer_called_with, string_buff_size)

    def test_tsget_success(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsget = MagicMock()
        MagicMock.return_value = 100
        return_value = tslib.tsget(tp_name, string_buff_size)
        self.assertEqual(return_value, (b'', b'testTuple'))
        tp_name_called_with = ctypes.create_string_buffer(2*len(tp_name))
        tp_name_called_with.value = tp_name.encode('utf-8')
        string_buffer_called_with = ctypes.create_string_buffer(string_buff_size)
        tslib.libso.tsget.assert_called_with(tp_name_called_with, string_buffer_called_with, string_buff_size)

    def test_tsget_failure(self):
        tp_name = "testTuple"
        string_buff_size = 100
        tslib.libso.tsget = MagicMock()
        MagicMock.return_value = 101
        return_value = tslib.tsget(tp_name, string_buff_size)
        self.assertEqual(return_value, 1)
        tp_name_called_with = ctypes.create_string_buffer(2*len(tp_name))
        tp_name_called_with.value = tp_name.encode('utf-8')
        string_buffer_called_with = ctypes.create_string_buffer(string_buff_size)
        tslib.libso.tsget.assert_called_with(tp_name_called_with, string_buffer_called_with, string_buff_size)


if __name__ == '__main__':
    unittest.main()

