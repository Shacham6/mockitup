import unittest.mock
from trace import Trace
from typing import Any, List, Mapping, Tuple, Type, TypeVar, cast

from typing_extensions import Protocol

from .actions import ActionRaises, ActionResultBase, ActionReturns, ActionYieldsFrom
from .arguments_matcher import ANY_ARG, ANY_ARGS, ArgumentsMatcher, ArgumentsMatchResult
from .proxies import MockResponseProxy

_MockType = TypeVar("_MockType", bound=unittest.mock.Mock)


def compose(mock: _MockType) -> "MockComposer":
    return MockComposer(mock)


class _MockComposerMembers:

    def __init__(self, mock: _MockType) -> None:
        self.mock = mock


def _composer_members(composer: "MockComposer") -> _MockComposerMembers:
    return cast(_MockComposerMembers, object.__getattribute__(composer, "_members"))


class MockComposer:

    def __init__(self, mock: _MockType):
        super().__setattr__("_members", _MockComposerMembers(mock))

    def __getattr__(self, name: str) -> "MockComposer":
        mock = _composer_members(self).mock
        result = getattr(mock, name)
        return MockComposer(result)

    def __setattr__(self, name: str, value: Any) -> None:
        members = _composer_members(self)
        return members.mock.__setattr__(name, value)

    def __enter__(self) -> "MockComposer":
        """
        Exists for fun. It'll look good that way.
        """
        return self

    def __exit__(self, exception_type: Type[BaseException], exception_value: BaseException, traceback: Trace) -> None:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> MockResponseProxy:
        members = _composer_members(self)
        return MockResponseProxy(
            members.mock,
            ArgumentsMatcher(args, kwargs),
            register_call_side_effect,
        )


def register_call_side_effect(mock: _MockType, arguments: ArgumentsMatcher, action: ActionResultBase) -> None:
    if not mock.side_effect:
        mock.side_effect = MockItUpSideEffect()
    mock.side_effect.register(arguments, action)


class MockItUpSideEffect:
    __registered: List[Tuple[ArgumentsMatcher, ActionResultBase]]

    def __init__(self) -> None:
        self.__registered = []

    def register(self, arguments: ArgumentsMatcher, action_result: ActionResultBase) -> None:
        self.__registered.append((arguments, action_result))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        results = []
        for registered_args, action_result in self.__registered:
            match_results = registered_args.matches(cast(Tuple[Any], args), kwargs)

            if not match_results:
                results.append(match_results)
                continue

            return action_result.provide_result()
        raise UnregisteredCall(results)


class UnregisteredCall(Exception):

    def __init__(self, failed_matches: List[ArgumentsMatchResult]):
        Exception.__init__(self, "Failed all arguments matching, can't finish call")
        self.failed_matches = failed_matches
