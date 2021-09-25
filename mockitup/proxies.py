import abc
from functools import partial
from typing import Any, Callable, Generic, Mapping, MutableMapping, Optional, Type, TypeVar
from unittest.mock import Mock

from typing_extensions import Concatenate, ParamSpec, Protocol

from .actions import ActionRaises, ActionReturns, ActionYieldsFrom, BaseActionResult
from .arguments_matcher import ArgumentsMatcher

_MockType = TypeVar("_MockType", bound=Mock)


class ProxyCallback(Protocol):

    def __call__(self, mock: _MockType, arguments: ArgumentsMatcher, action: BaseActionResult) -> None:
        ...


class _ActionResultBaseFactory(Protocol):

    def __call__(self, value: Any) -> BaseActionResult:
        ...


class _ValueProvidingDescriptor:

    def __init__(self, build_action_result: _ActionResultBaseFactory) -> None:
        self.__build_action_result = build_action_result

    def __get__(
        self,
        obj: "MockResponseProxy",
        objtype: Optional[Type["MockResponseProxy"]] = None,
    ) -> Callable[[Any], None]:

        def __tmp(value: Any) -> None:
            return obj._cb(
                obj._mock,
                obj._arguments,
                self.__build_action_result(value),
            )

        return __tmp


class _ValueProvidingDescriptorWithDefaultValue(_ValueProvidingDescriptor):

    def __init__(self, build_action_result: _ActionResultBaseFactory, default_value: Any) -> None:
        self.__build_action_result = build_action_result
        self.__default_value = default_value

    def __get__(
        self,
        obj: "MockResponseProxy",
        objtype: Optional[Type["MockResponseProxy"]] = None,
    ) -> Callable[[Any], None]:
        _none = object()

        def __tmp(value: Any = _none) -> None:
            return obj._cb(
                obj._mock,
                obj._arguments,
                self.__build_action_result(value) if value is not _none else self.__default_value,
            )

        return __tmp


class MockResponseProxy:

    def __init__(self, mock: _MockType, arguments: "ArgumentsMatcher", cb: ProxyCallback):
        self._mock = mock
        self._arguments = arguments
        self._cb = cb

    def returns(self, value: Any = None) -> None:
        return self._cb(self._mock, self._arguments, ActionReturns(value))

    raises = _ValueProvidingDescriptor(ActionRaises)
    yields_from = _ValueProvidingDescriptor(ActionYieldsFrom)
