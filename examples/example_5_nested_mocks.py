from unittest.mock import Mock

from mockitup import expectation_suite
from typing_extensions import Protocol


class NumberGetter(Protocol):
    def get_number(self) -> int: ...


class Printer(Protocol):
    def print_number(self, number: int) -> None: ...


def print_if_number_is_odd(number_getter: NumberGetter, printer: Printer):
    number = number_getter.get_number()
    if number % 2 == 1:
        printer.print_number(number)


def mocks_inside_mocks_example():
    with expectation_suite() as es:
        mock = Mock()
        es.expect(mock).number_getter.get_number().returns(1)
        es.expect(mock).printer.print_number(1).returns()

        print_if_number_is_odd(mock.number_getter, mock.printer)
