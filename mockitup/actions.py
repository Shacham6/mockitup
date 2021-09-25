import unittest.mock
from typing import Any, Iterable, TypeVar

from typing_extensions import Protocol

_MockType = TypeVar("_MockType", bound=unittest.mock.Mock)


class BaseActionResult(Protocol):

    def provide_result(self) -> Any:
        ...


class ActionReturnsMultipleValues:

    def __init__(self, *values: Any):
        self.__return_none = len(values) == 0
        self.__values = iter(values)
        self.__last_value = None

    def provide_result(self) -> Any:
        if self.__return_none:
            return None
        try:
            self.__last_value = next(self.__values)
        except StopIteration:
            pass
        return self.__last_value


class ActionReturnsSingleValue:

    def __init__(self, value: Any):
        self.__value = value

    def provide_result(self) -> Any:
        return self.__value

    def __eq__(self, o: object) -> bool:
        return bool(self.__value == o)


class ActionRaises:

    def __init__(self, value: Any):
        self.__value = value

    def provide_result(self) -> Any:
        raise self.__value


class ActionYieldsFrom:

    def __init__(self, value: Iterable[Any]):
        self.__value = value

    def provide_result(self) -> Any:
        yield from self.__value
