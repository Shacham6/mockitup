from unittest.mock import MagicMock

import pytest
from hamcrest import equal_to, greater_than
from mockitup.composer import ANY_ARG, ArgumentsMatcher, MethodProxy, MockComposer, compose, register_call_side_effect


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
