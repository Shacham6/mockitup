import abc
import unittest.mock
from collections import namedtuple
from typing import Any, Callable, Mapping, Protocol, Tuple, TypeVar

import hamcrest
from hamcrest.core.matcher import Matcher


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
        return MethodProxy(
            members.mock,
            StrictArgs(args, kwargs),
            register_call_side_effect,
        )


class MethodProxy:

    def __init__(self, mock, arguments: "ArgsBase", cb):
        self._mock = mock
        self._arguments = arguments
        self._cb = cb

    def returns(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionReturns(value))


class ArgsBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def matches(self, args: Tuple[Any], kwargs: Mapping[str, Any]) -> bool:
        pass


ANY_ARG = object()
ANY_ARGS = object()


class StrictArgs(ArgsBase, namedtuple("StrictArgs", ["args", "kwargs"])):

    def matches(self, args: Tuple[Any], kwargs: Mapping[str, Any]) -> bool:
        registered_len = len(self.args) + len(self.kwargs)
        provided_len = len(args) + len(kwargs)
        if registered_len == provided_len == 0:
            return True

        if registered_len != provided_len:
            return False

        if self.args[0] is ANY_ARGS:
            return True

        args_equal = any(self.__match_values(registered, provided) for registered, provided in zip(self.args, args))
        if not args_equal:
            return False

        # Should have same keys
        if set(self.kwargs) != set(kwargs):
            return False

        for key in self.kwargs:
            if not self.__match_values(self.kwargs[key], kwargs[key]):
                return False
        return True

    @staticmethod
    def __match_values(registered_value, provided_value) -> bool:
        if registered_value is ANY_ARG:
            return True

        if isinstance(registered_value, Matcher):
            registered_value = hamcrest.match_equality(registered_value)

        return registered_value == provided_value


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


def register_call_side_effect(mock: unittest.mock.MagicMock, arguments, action_result):
    if not mock.side_effect:
        mock.side_effect = MockItUpSideEffect()
    mock.side_effect.register(arguments, action_result)


class MockItUpSideEffect:

    def __init__(self):
        self.__registered = []

    def register(self, arguments, action_result):
        self.__registered.append((arguments, action_result))

    def __call__(self, *args, **kwargs):
        for registered_args, action_result in self.__registered:
            if registered_args.matches(args, kwargs):
                return action_result.provide_result()
        raise UnregisteredCall()


class UnregisteredCall(Exception):
    pass
