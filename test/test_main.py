from rx import operators as ops

import unittest
from unittest.mock import Mock

from main import main


shop_picker_input_mock = Mock()
shop_picker_input_mock.return_value = '1,2'


class Main(unittest.TestCase):
    def test_main_func_should_return_a_no_empty_stream(self):
        sub = main('tv', shop_picker_input_mock)
        products = sub.pipe(
            ops.to_list()
        ).run()

        sub.connect()
        self.assertGreater(len(products), 0)

