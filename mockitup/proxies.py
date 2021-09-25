from typing import Any, Callable, Mapping, MutableMapping, Optional, Type, TypeVar
from unittest.mock import Mock

from typing_extensions import Protocol

from .actions import ActionRaises, ActionResultBase, ActionReturns, ActionYieldsFrom
from .arguments_matcher import ArgumentsMatcher

_MockType = TypeVar("_MockType", bound=Mock)


class _ProxyCallback(Protocol):

    def __call__(self, mock: _MockType, arguments: ArgumentsMatcher, action: ActionResultBase) -> None:
        ...


class _ActionResultBaseFactory(Protocol):

    def __call__(self, value: Any) -> ActionResultBase:
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


class MockResponseProxy:

    def __init__(self, mock: _MockType, arguments: "ArgumentsMatcher", cb: _ProxyCallback):
        self._mock = mock
        self._arguments = arguments
        self._cb = cb

    returns = _ValueProvidingDescriptor(ActionReturns)
    raises = _ValueProvidingDescriptor(ActionRaises)
    yields_from = _ValueProvidingDescriptor(ActionYieldsFrom)
