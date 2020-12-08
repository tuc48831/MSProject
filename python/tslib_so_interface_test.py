import unittest
from unittest.mock import MagicMock

import tslib_so_interface as tslib


class MyTestCase(unittest.TestCase):

    def test_tsput(self):
        tp_name = "testTuple"
        tp_value = "This is the tuple value"
        tp_size = 100
        tslib.tsput = MagicMock()
        MagicMock.return_value = 0
        return_value = tslib.tsput(tp_name, tp_value, tp_size)
        self.assertEqual(return_value, 0)
        tslib.tsput.assert_called_with(tp_name, tp_value, tp_size)


if __name__ == '__main__':
    unittest.main()

