import unittest
from unittest.mock import Mock

from src.scraping_demo import show_shops, get_property


mocked_parent = Mock()
mocked_child = Mock()

mocked_parent.find_element_by_xpath.return_value = mocked_child

config_mock = {'magazine': {}, 'americanas': {}, 'amazon': {}}


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
        self.assertRegex(show_shops(config_mock), '\[\d+\]\s\w+\n\[\d+\]\s\w+\n\[\d+\]\s\w+')
