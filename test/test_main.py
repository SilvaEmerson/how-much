from rx import operators as ops

import unittest
from unittest.mock import Mock

from main import main


shop_picker_input_mock = Mock()
shop_picker_input_mock.return_value = "1"
search_term_input_mock = "notebook"


class Main(unittest.TestCase):
    def test_should_return_no_empty_observable(self):
        products = main(search_term_input_mock, shop_picker_input_mock)
        products.subscribe(lambda res: self.assertGreater(len(res), 0))
        products.connect()
