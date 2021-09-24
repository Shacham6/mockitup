import unittest.mock
from typing import Any, List

from .actions import ActionRaises, ActionResultBase, ActionReturns, ActionYieldsFrom
from .arguments_matcher import ANY_ARG, ANY_ARGS, ArgumentsMatcher, ArgumentsMatchResult


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
            ArgumentsMatcher(args, kwargs),
            register_call_side_effect,
        )


class MethodProxy:

    def __init__(self, mock, arguments: "ArgumentsMatcher", cb):
        self._mock = mock
        self._arguments = arguments
        self._cb = cb

    def returns(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionReturns(value))

    def yields_from(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionYieldsFrom(value))

    def raises(self, value: Any) -> None:
        self._cb(self._mock, self._arguments, ActionRaises(value))


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
        results = []
        for registered_args, action_result in self.__registered:
            match_results = registered_args.matches(args, kwargs)

            if not match_results:
                results.append(match_results)
                continue

            return action_result.provide_result()
        raise UnregisteredCall(results)


class UnregisteredCall(Exception):

    def __init__(self, failed_matches: List[ArgumentsMatchResult]):
        Exception.__init__(self, "Failed all arguments matching, can't finish call")
        self.failed_matches = failed_matches
