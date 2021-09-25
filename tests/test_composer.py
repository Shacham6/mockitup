from unittest.mock import MagicMock

import pytest
from hamcrest import equal_to, greater_than
from mockitup.composer import ANY_ARG, ArgumentsMatcher, ExpectationNotMet, MockComposer, MockResponseProxy, \
    expectation_suite


def test_compose_allows_nesting():
    mock = MagicMock()
    with expectation_suite() as es:
        assert isinstance(es.allow(mock).a.b.c, MockComposer)
        assert isinstance(es.allow(mock).a.b.c(), MockResponseProxy)


def test_compose_calls_program_results_for_arguments():
    with expectation_suite() as es:
        mock = MagicMock()
        es.allow(mock).a.b.c = 5
        assert mock.a.b.c == 5


def test_nested_composing_using_with():
    with expectation_suite() as es:
        mock = MagicMock()
        with es.allow(mock).a as a:
            a.b = 5
            a.c = 6

        assert mock.a.b == 5
        assert mock.a.c == 6


def test_compose_uses_primary_side_effect_function():
    with expectation_suite() as es:
        mock = MagicMock()
        es.allow(mock).get_five().returns(5)
        assert mock.get_five() == 5

        with es.allow(mock.add_five) as add_five:
            add_five(5).returns(10)
            add_five(6).returns(11)
        assert mock.add_five(5) == 10
        assert mock.add_five(6) == 11


def test_wildcards():
    with expectation_suite() as es:
        mock = MagicMock()
        es.allow(mock).tell_me_something(ANY_ARG).returns("That's interesting")
        assert mock.tell_me_something("Hello") == "That's interesting"


def test_hamcrest_patterns():
    with expectation_suite() as es:
        mock = MagicMock()
        es.allow(mock).add_five(equal_to(5)).returns(10)
        es.allow(mock).add_five(greater_than(10)).returns(-1)
        assert mock.add_five(5) == 10
        assert mock.add_five(11) == -1
        assert mock.add_five(12) == -1


def test_yields():
    with expectation_suite() as es:
        mock = MagicMock()
        es.allow(mock).iter_numbers().yields_from([1, 2, 3, 4, 5])

        return_value = mock.iter_numbers()
        assert not isinstance(return_value, list)
        assert list(return_value) == [1, 2, 3, 4, 5]


def test_raises():
    with expectation_suite() as es:
        mock = MagicMock()
        with es.allow(mock.divide) as divide:
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
