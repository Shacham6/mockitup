from unittest.mock import MagicMock

from mockitup.composer import MethodProxy, MockComposer, StrictArgs, compose, register_call_side_effect


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
    mproxy = MethodProxy(mock, StrictArgs(tuple(), {}), cb)
    mproxy.returns(5)

    assert cb_called


def test_composer_calls_provide_call_spec():
    calls = []

    def cb(mock, arguments, action_result):
        calls.append((mock, arguments, action_result))

    mock = MagicMock()
    mproxy = MethodProxy(mock, StrictArgs(tuple(), {}), cb)
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
        StrictArgs(tuple(), {}),
        register_call_side_effect,
    ).returns(5)

    MethodProxy(
        mock.get_six,
        StrictArgs(tuple(), {}),
        register_call_side_effect,
    ).returns(6)

    assert mock.get_five() == 5
    assert mock.get_six() == 6
