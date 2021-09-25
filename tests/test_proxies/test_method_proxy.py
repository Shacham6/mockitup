from unittest.mock import MagicMock

from mockitup.composer import ArgumentsMatcher, MockResponseProxy


def test_method_proxy_callback():
    cb_called = False

    def cb(*args, **kwargs):
        nonlocal cb_called
        cb_called = True

    mock = MagicMock()
    mproxy = MockResponseProxy(mock, ArgumentsMatcher(tuple(), {}), cb)
    mproxy.returns(5)

    assert cb_called


def test_composer_calls_provide_call_spec():
    calls = []

    def cb(mock, arguments, action_result):
        calls.append((mock, arguments, action_result))

    mock = MagicMock()
    mproxy = MockResponseProxy(mock, ArgumentsMatcher(tuple(), {}), cb)
    mproxy.returns(5)

    assert len(calls) == 1
    call = calls[0]
    # Since no arguments were really provided
    originated_mock, arguments, action_result = call
    assert originated_mock is mock
    assert arguments == (tuple(), {})
    assert action_result.provide_result() == 5
