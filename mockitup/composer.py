from typing import Any, Callable, Mapping, Protocol, Tuple, TypeVar
import unittest.mock


def compose(mock: unittest.mock.MagicMock) -> "MockComposer":
    return MockComposer(mock)


class _MockComposerMembers:

    def __init__(self, mock):
        self.mock = mock


def _composer_members(composer) -> _MockComposerMembers:
    return object.__getattribute__(composer, "_members")


class MockComposer:

    def __init__(self, mock: unittest.mock.MagicMock):
        super().__setattr__("_members", _MockComposerMembers(mock))

    def __getattr__(self, name: str) -> "MockComposer":
        mock = _composer_members(self).mock
        result = getattr(mock, name)
        return MockComposer(result)

    def __setattr__(self, name: str, value: Any):
        members = _composer_members(self)
        return members.mock.__setattr__(name, value)

    def __enter__(self) -> "MockComposer":
        """
        Exists for fun. It'll look good that way.
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def __call__(self, *args, **kwargs) -> "MethodProxy":
        members = _composer_members(self)
        return MethodProxy(members.mock, args, kwargs, None)


_T = TypeVar("_T")


class MethodProxy:

    def __init__(self, mock, args: Tuple, kwargs: Mapping, cb):
        self._mock = mock
        self._args = args
        self._kwargs = kwargs
        self._cb = cb

    def returns(self, value: Any) -> None:
        self._cb(self._mock, (self._args, self._kwargs), ActionReturns(value))


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
