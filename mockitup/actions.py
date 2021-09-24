import unittest.mock
from typing import Any, Iterable, List, Protocol

from .arguments_matcher import ANY_ARG, ANY_ARGS, ArgumentsMatcher, ArgumentsMatchResult


class ActionResultBase(Protocol):

    def provide_result(self) -> Any:
        ...


class ActionReturns:

    def __init__(self, value: Any):
        self.__value = value

    def provide_result(self) -> Any:
        return self.__value

    def __eq__(self, o: object) -> bool:
        return self.__value == o


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
