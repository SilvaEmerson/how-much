import unittest
from unittest.mock import Mock
import json

from src.operations import show_shops, get_property, search_product


with open("./config.json", "r") as shops_config:
    config = json.load(shops_config)


mocked_parent = Mock()
mocked_child = Mock()

mocked_parent.find_element_by_xpath.return_value = mocked_child

config_mock = {"magazine": {}, "americanas": {}, "amazon": {}}
shops_list = [0]
search_term_input_mock = "notebook"


class Main(unittest.TestCase):
    def test_get_property_should_return_demo(self):
        mocked_child.text = "demo"
        self.assertEqual(get_property(mocked_parent, ""), "demo")

    def test_get_property_should_return_empty_string(self):
        mocked_parent.find_element_by_xpath.return_value = None
        self.assertEqual(get_property(mocked_parent, ""), "")

    def test_show_shops_should_return_a_not_empty_string(self):
        self.assertGreater(len(show_shops(config_mock)), 0)

    def test_show_shops_should_be_almost_equal_to_expected_string(self):
        self.assertRegex(
            show_shops(config_mock),
            r"\[\d+\]\s\w+\n\[\d+\]\s\w+\n\[\d+\]\s\w+",
        )

    def test_should_return_no_empty_observable(self):
        for id, shop_name in enumerate(config):
            shop_picker_input_mock = Mock(return_value=f"{id}")
            products = search_product(
                search_term_input_mock, shops_list, shop_picker_input_mock, CONFIG=config_mock
            )
            products.subscribe(
                lambda res: self.assertGreater(
                    len(res), 0, msg=f"{shop_name} return nothing"
                )
            )
            products.connect()
