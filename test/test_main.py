from rx import operators as ops

import unittest
from unittest.mock import Mock

from main import main


shop_picker_input_mock = Mock()
shop_picker_input_mock.return_value = '1,2'


class Main(unittest.TestCase):
    pass
