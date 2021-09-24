from unittest.mock import MagicMock

from mockitup.composer import MethodProxy, MockComposer, ArgumentsMatcher, compose, register_call_side_effect, ANY_ARG
from hamcrest import equal_to, greater_than


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


def test_method_proxy_callback():
    cb_called = False

    def cb(*args, **kwargs):
        nonlocal cb_called
        cb_called = True

    mock = MagicMock()
    mproxy = MethodProxy(mock, ArgumentsMatcher(tuple(), {}), cb)
    mproxy.returns(5)

    assert cb_called


def test_composer_calls_provide_call_spec():
    calls = []

    def cb(mock, arguments, action_result):
        calls.append((mock, arguments, action_result))

    mock = MagicMock()
    mproxy = MethodProxy(mock, ArgumentsMatcher(tuple(), {}), cb)
    mproxy.returns(5)

    assert len(calls) == 1
    call = calls[0]
    # Since no arguments were really provided
    originated_mock, arguments, action_result = call
    assert originated_mock is mock
    assert arguments == (tuple(), {})
    assert action_result.provide_result() == 5


def test_super_thingy_callback_registers_calls():
    mock = MagicMock()

    MethodProxy(
        mock.get_five,
        ArgumentsMatcher(tuple(), {}),
        register_call_side_effect,
    ).returns(5)

    MethodProxy(
        mock.get_six,
        ArgumentsMatcher(tuple(), {}),
        register_call_side_effect,
    ).returns(6)

    assert mock.get_five() == 5
    assert mock.get_six() == 6


def test_results_per_arguments():
    mock = MagicMock()
    MethodProxy(mock.add_five, ArgumentsMatcher((5,), {}), register_call_side_effect).returns(10)
    MethodProxy(mock.add_five, ArgumentsMatcher((6,), {}), register_call_side_effect).returns(11)
    assert mock.add_five(5) == 10
    assert mock.add_five(6) == 11


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
