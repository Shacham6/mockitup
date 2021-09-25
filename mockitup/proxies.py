from typing import Any, Callable, TypeVar
from unittest.mock import Mock

from typing_extensions import Protocol

from .actions import ActionRaises, ActionResultBase, ActionReturns, ActionYieldsFrom
from .arguments_matcher import ArgumentsMatcher

_MockType = TypeVar("_MockType", bound=Mock)


class _ProxyCallback(Protocol):

    def __call__(self, mock: _MockType, arguments: ArgumentsMatcher, action: ActionResultBase) -> None:
        ...


class MethodProxy:

    def __init__(self, mock: _MockType, arguments: "ArgumentsMatcher", cb: _ProxyCallback):
        self._mock = mock
        self._arguments = arguments
        self._cb = cb

    def returns(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionReturns(value))

    def yields_from(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionYieldsFrom(value))

    def raises(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionRaises(value))
