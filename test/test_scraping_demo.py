import unittest
from unittest.mock import Mock

from src.scraping_demo import get_property


mocked_parent = Mock()
mocked_child = Mock()

mocked_parent.find_element_by_xpath.return_value = mocked_child


class Main(unittest.TestCase):
    def test_get_property_should_return_demo(self):
        mocked_child.text = 'demo'
        self.assertEqual(get_property(mocked_parent, ''), 'demo')

    def test_get_property_should_return_empty_string(self):
        mocked_parent.find_element_by_xpath.return_value = None
        self.assertEqual(get_property(mocked_parent, ''), '')
