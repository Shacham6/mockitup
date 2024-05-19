from unittest.mock import Mock, call

from mockitup import expectation_suite
from typing_extensions import Protocol


class NumberGetter(Protocol):
    def get(self, number_name: str) -> int: ...


def weird_get_five(number_getter: NumberGetter) -> int:
    return number_getter.get("two") + number_getter.get("three")


def vanilla_verbose_mocking_example():
    number_getter_mock = Mock()

    def get_mock(number_name: str) -> int:
        return {"two": 2, "three": 3}[number_name]

    number_getter_mock.get.side_effect = get_mock

    assert weird_get_five(number_getter_mock) == 5

    number_getter_mock.get.assert_any_call("two")
    number_getter_mock.get.assert_any_call("three")


def vanilla_shorter_mocking_example():
    def get_mock(number_name: str) -> int:
        return {"two": 2, "three": 3}[number_name]

    number_getter_mock = Mock(**{"get.side_effect": get_mock})

    assert weird_get_five(number_getter_mock) == 5

    number_getter_mock.get.assert_has_calls([call("two"), call("three")])


def mockitup_example():
    with expectation_suite() as es:
        mock = Mock()
        es.expect(mock).get("two").returns(2)
        es.expect(mock).get("three").returns(3)

        assert weird_get_five(mock) == 5
