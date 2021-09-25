import unittest.mock
from trace import Trace
from typing import Any, List, Optional, Tuple, Type, TypeVar, cast

from typing_extensions import Protocol

from .actions import BaseActionResult
from .arguments_matcher import ArgumentsMatcher, ArgumentsMatchResult
from .proxies import MockResponseProxy, ProxyCallback

_MockType = TypeVar("_MockType", bound=unittest.mock.Mock)


class _MockComposerMembers:

    def __init__(self, mock: _MockType, proxy_cb: ProxyCallback) -> None:
        self.mock = mock
        self.proxy_cb: ProxyCallback = proxy_cb


def _composer_members(composer: "MockComposer") -> _MockComposerMembers:
    return cast(_MockComposerMembers, object.__getattribute__(composer, "_members"))


class MockComposer:

    def __init__(self, mock: _MockType, proxy_cb: ProxyCallback):
        super().__setattr__("_members", _MockComposerMembers(mock, proxy_cb))

    def __getattr__(self, name: str) -> "MockComposer":
        members = _composer_members(self)
        mock = members.mock
        result = getattr(mock, name)
        return MockComposer(result, members.proxy_cb)

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
            members.proxy_cb,
        )


class ExpectationFulfillmentCursor:

    def __init__(self) -> None:
        self.__cursor = 0

    def next(self) -> int:
        curr = self.__cursor
        self.__cursor += 1
        return curr


class ExpectationSuite:
    __expectations: List["__Expectation"]
    __ordered: bool

    def __init__(self, ordered: bool) -> None:
        self.__expectations = []
        self.__ordered = ordered
        self.__expectation_fulfillment_cursor = ExpectationFulfillmentCursor()

    def __enter__(self) -> "ExpectationSuite":
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.__validate_expectations()

    def __validate_expectations(self) -> None:
        for expectation_index, expectation in enumerate(self.__expectations):
            expectation.assert_met()
            if self.__ordered and expectation_index != expectation.fulfillment_step:
                raise ExpectationNotMet("Expectations were fulfilled out of order")

    def expect(self, mock: _MockType) -> "MockComposer":
        return MockComposer(mock, self.__register_expectation)

    def __register_expectation(
        self,
        mock: _MockType,
        arguments: ArgumentsMatcher,
        action: BaseActionResult,
    ) -> None:
        expectation = self.__Expectation(mock, arguments, self.__expectation_fulfillment_cursor)
        self.__register_call_side_effect(mock, arguments, action, report=expectation.finish)
        self.__expectations.append(expectation)

    def allow(self, mock: _MockType) -> "MockComposer":
        return MockComposer(mock, self.__register_allowance)

    def __register_allowance(
        self,
        mock: _MockType,
        arguments: ArgumentsMatcher,
        action: BaseActionResult,
    ) -> None:
        self.__register_call_side_effect(mock, arguments, action, report=lambda *args: None)

    def __register_call_side_effect(
        self,
        mock: _MockType,
        arguments: ArgumentsMatcher,
        action: BaseActionResult,
        *,
        report: "_ReportMatchResults",
    ) -> None:
        if not mock.side_effect:
            mock.side_effect = MockItUpSideEffect()

        mock.side_effect.register(arguments, action, report=report)

    class __Expectation:
        __match_results: Optional[ArgumentsMatchResult]
        __fulfilled_at_step: Optional[int]

        def __init__(self, mock: _MockType, args: ArgumentsMatcher,
                     fulfillment_cursor: ExpectationFulfillmentCursor) -> None:
            self.__mock = mock
            self.__args = args
            self.__match_results = None
            self.__fulfillment_cursor = fulfillment_cursor
            self.__fulfilled_at_step = None

        def was_met(self) -> bool:
            return bool(self.__match_results)

        def assert_met(self) -> None:
            if not self.__match_results:
                mock_name = self.__mock._extract_mock_name()
                args, kwargs = self.__args
                message = (f"Expected mock `{mock_name}` to be called with "
                           f"(args: '{args}', kwargs: '{kwargs}'), but wasn't")
                raise ExpectationNotFulfilled(
                    message,
                    mock=self.__mock,
                    expected_arguments=self.__args,
                )

        def finish(self, match_results: ArgumentsMatchResult) -> None:
            self.__match_results = match_results
            self.__fulfilled_at_step = self.__fulfillment_cursor.next()

        @property
        def fulfillment_step(self) -> Optional[int]:
            return self.__fulfilled_at_step


class _ReportMatchResults(Protocol):

    def __call__(self, match_results: ArgumentsMatchResult) -> None:
        ...


class _ExpectationResult:
    pass


def expectation_suite(ordered: bool = False) -> ExpectationSuite:
    return ExpectationSuite(ordered=ordered)


class ExpectationNotMet(Exception):
    pass


class ExpectationNotFulfilled(ExpectationNotMet):

    def __init__(
        self,
        *args: object,
        mock: _MockType,
        expected_arguments: ArgumentsMatcher,
    ) -> None:
        Exception.__init__(self, *args)
        self.mock = mock
        self.expected_arguments = expected_arguments


class ExpectationOutOfOrder(ExpectationNotMet):
    pass


class MockItUpSideEffect:
    __registered: List[Tuple[ArgumentsMatcher, BaseActionResult, _ReportMatchResults]]

    def __init__(self) -> None:
        self.__registered = []

    def register(self, arguments: ArgumentsMatcher, action_result: BaseActionResult,
                 report: _ReportMatchResults) -> None:
        self.__registered.append((arguments, action_result, report))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        results = []
        for registered_args, action_result, report in self.__registered:
            match_results = registered_args.matches(cast(Tuple[Any], args), kwargs)

            if not match_results:
                results.append(match_results)
                continue

            report(match_results)
            return action_result.provide_result()
        raise UnregisteredCall(results)


class UnregisteredCall(Exception):

    def __init__(self, failed_matches: List[ArgumentsMatchResult]):
        Exception.__init__(self, "Failed all arguments matching, can't finish call")
        self.failed_matches = failed_matches
