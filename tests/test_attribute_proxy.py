import pytest
from mockitup.attr_proxy import MethProxy
from mockitup.mock import Mock


def test_mock_returns_proxies_while_recording():
    with Mock() as mock:
        assert isinstance(mock.something, MethProxy)

    with pytest.raises(ValueError):
        mock.something_else


def test_can_set_properties():
    with Mock() as mock:
        mock.something = 5

    assert mock.something == 5
    with pytest.raises(ValueError):
        mock.something_else


def test_attr_proxy_sends_cb():
    was_cb_called = False

    def meth_cb(*args, **kwargs):
        nonlocal was_cb_called
        was_cb_called = True

    proxy = MethProxy("get_five", meth_cb=meth_cb)
    proxy().returns(5)

    assert was_cb_called
