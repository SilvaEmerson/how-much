from rx import operators as ops

from unittest.mock import Mock
import unittest
import json

from main import search_product


with open("./config.json", "r") as shops_config:
    config = json.load(shops_config)


shop_picker_input_mock = Mock()
search_term_input_mock = "notebook"


class Main(unittest.TestCase):
    def test_should_return_no_empty_observable(self):
        for id, shop_name in enumerate(config):
            shop_picker_input_mock = Mock(return_value=f"{id}")
            products = search_product(search_term_input_mock, [0], shop_picker_input_mock, CONFIG=config)
            products.subscribe(
                lambda res: self.assertGreater(
                    len(res), 0, msg=f"{shop_name} return nothing"
                )
            )
            products.connect()
