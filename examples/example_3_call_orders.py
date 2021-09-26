from unittest.mock import Mock, call

import pytest
from mockitup import allow, expectation_suite
from mockitup.composer import ExpectationNotMet


def vanilla_mock_orderered_calls_example():
    mock = Mock()
    mock("zero")
    mock.get("one")
    mock.get("two")
    mock.get_three()

    assert mock.mock_calls == [
        call("zero"),
        call.get("one"),
        call.get("two"),
        call.get_three(),
    ]

    # Here I have omitted the first call
    assert mock.mock_calls != [
        call.get("one"),
        call.get("two"),
        call.get_three(),
    ]


def mockitup_ordered_calls_using_expectations_example():
    with expectation_suite(ordered=True) as es:
        mock = Mock()
        es.expect(mock).__call__("zero").returns()
        es.expect(mock).get("one").returns()
        es.expect(mock).get("two").returns()
        es.expect(mock).get_three().returns()

        mock("zero")
        mock.get("one")
        mock.get("two")
        mock.get_three()

    with pytest.raises(ExpectationNotMet):
        with expectation_suite(ordered=True) as es:
            mock = Mock()
            es.expect(mock).__call__("zero").returns()
            es.expect(mock).get("one").returns()
            es.expect(mock).get("two").returns()
            es.expect(mock).get_three().returns()

            mock("zero")
            mock.get("one")
            # Here I omitted the call `mock.get("two")`
            mock.get_three()
            mock.get("two")


def mockitup_mixed_with_unittest_mock_example():
    mock = Mock()
    allow(mock).__call__("zero").returns()
    allow(mock).get("one").returns()
    allow(mock).get_two().returns()

    mock("zero")
    mock.get("one")
    mock.get_two()

    assert mock.mock_calls == [
        call("zero"),
        call.get("one"),
        call.get_two(),
    ]
