from unittest.mock import MagicMock, Mock

import pytest
from hamcrest import equal_to, greater_than
from mockitup import ANY_ARG, allow
from mockitup.composer import ExpectationNotMet, MockComposer, MockResponseProxy, expectation_suite


def test_compose_allows_nesting():
    mock = MagicMock()
    assert isinstance(allow(mock).a.b.c, MockComposer)
    assert isinstance(allow(mock).a.b.c(), MockResponseProxy)


def test_compose_calls_program_results_for_arguments():
    mock = MagicMock()
    allow(mock).a.b.c = 5
    assert mock.a.b.c == 5


def test_nested_composing_using_with():
    mock = MagicMock()
    with allow(mock).a as a:
        a.b = 5
        a.c = 6

    assert mock.a.b == 5
    assert mock.a.c == 6


def test_compose_uses_primary_side_effect_function():
    mock = MagicMock()
    allow(mock).get_five().returns(5)
    assert mock.get_five() == 5

    with allow(mock.add_five) as add_five:
        add_five(5).returns(10)
        add_five(6).returns(11)
    assert mock.add_five(5) == 10
    assert mock.add_five(6) == 11


def test_wildcards():
    mock = MagicMock()
    allow(mock).tell_me_something(ANY_ARG).returns("That's interesting")
    assert mock.tell_me_something("Hello") == "That's interesting"


def test_hamcrest_patterns():
    mock = MagicMock()
    allow(mock).add_five(equal_to(5)).returns(10)
    allow(mock).add_five(greater_than(10)).returns(-1)
    assert mock.add_five(5) == 10
    assert mock.add_five(11) == -1
    assert mock.add_five(12) == -1


def test_yields():
    mock = MagicMock()
    allow(mock).iter_numbers().yields_from([1, 2, 3, 4, 5])

    return_value = mock.iter_numbers()
    assert not isinstance(return_value, list)
    assert list(return_value) == [1, 2, 3, 4, 5]


def test_raises():
    mock = MagicMock()
    with allow(mock.divide) as divide:
        divide(ANY_ARG, 0).raises(ZeroDivisionError())
        divide(4, 2).returns(2)

    assert mock.divide(4, 2) == 2
    with pytest.raises(ZeroDivisionError):
        mock.divide(9, 0)
    with pytest.raises(ZeroDivisionError):
        mock.divide(8, 0)


def test_expect_raises_when_mock_spec_not_called():
    # Here we call the method we "programmed"
    with expectation_suite() as es:
        mock = MagicMock()
        es.expect(mock).get_six().returns(6)

        assert mock.get_six() == 6

    # Here we don't
    with pytest.raises(ExpectationNotMet):
        with expectation_suite() as es:
            mock = MagicMock()
            es.expect(mock).get_five().returns(5)


def test_expect_all_calls_for_same_mock():
    with expectation_suite() as es:
        mock = Mock()
        es.expect(mock).__call__("one").returns(1)
        es.expect(mock).__call__("two").returns(2)

        assert mock("one") + mock("two") == 3


def test_expect_ensures_order():
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
