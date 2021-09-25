from typing import Callable
from unittest.mock import Mock

from mockitup import expectation_suite


def add_five(number: int, get_five: Callable[[], int]):
    return number + get_five()


def simple_mock_vanilla_example():
    get_five = Mock()
    get_five.return_value = 5

    assert add_five(5, get_five) == 10

    get_five.assert_called_with()


def using_mockitup_example():
    with expectation_suite() as es:
        get_five = Mock()
        es.expect(get_five).__call__().returns(5)

        assert add_five(5, get_five)
