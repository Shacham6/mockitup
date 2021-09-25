from mockitup.composer import ExpectationNotMet
import pytest
from unittest.mock import Mock, call
from mockitup import expectation_suite


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


def mockitup_ordered_calls_example():
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
            mock.get_three()
            mock.get("two")
