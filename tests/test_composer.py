from unittest.mock import MagicMock

import pytest
from hamcrest import equal_to, greater_than
from mockitup.composer import ANY_ARG, ArgumentsMatcher, MethodProxy, MockComposer, compose, register_call_side_effect


def test_compose_allows_nesting():
    mock = MagicMock()
    assert isinstance(compose(mock).a.b.c, MockComposer)
    assert isinstance(compose(mock).a.b.c(), MethodProxy)


def test_compose_calls_program_results_for_arguments():
    mock = MagicMock()
    compose(mock).a.b.c = 5
    assert mock.a.b.c == 5


def test_nested_composing_using_with():
    mock = MagicMock()
    with compose(mock).a as a:
        a.b = 5
        a.c = 6

    assert mock.a.b == 5
    assert mock.a.c == 6


def test_compose_uses_primary_side_effect_function():
    mock = MagicMock()
    compose(mock).get_five().returns(5)
    assert mock.get_five() == 5

    with compose(mock.add_five) as add_five:
        add_five(5).returns(10)
        add_five(6).returns(11)
    assert mock.add_five(5) == 10
    assert mock.add_five(6) == 11


def test_wildcards():
    mock = MagicMock()
    compose(mock).tell_me_something(ANY_ARG).returns("That's interesting")
    assert mock.tell_me_something("Hello") == "That's interesting"


def test_hamcrest_patterns():
    mock = MagicMock()
    compose(mock).add_five(equal_to(5)).returns(10)
    compose(mock).add_five(greater_than(10)).returns(-1)
    assert mock.add_five(5) == 10
    assert mock.add_five(11) == -1
    assert mock.add_five(12) == -1


def test_yields():
    mock = MagicMock()
    compose(mock).iter_numbers().yields_from([1, 2, 3, 4, 5])

    return_value = mock.iter_numbers()
    assert not isinstance(return_value, list)
    assert list(return_value) == [1, 2, 3, 4, 5]


def test_raises():
    mock = MagicMock()
    with compose(mock.divide) as divide:
        divide(ANY_ARG, 0).raises(ZeroDivisionError())
        divide(4, 2).returns(2)

    assert mock.divide(4, 2) == 2
    with pytest.raises(ZeroDivisionError):
        mock.divide(9, 0)
    with pytest.raises(ZeroDivisionError):
        mock.divide(8, 0)
