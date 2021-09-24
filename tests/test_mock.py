import pytest
from mockitup.mock import Mock


def test_mock_raises_when_called_unconfigured():
    mock = Mock()
    with pytest.raises(ValueError):
        mock.get_five()


def test_mock_returns_assigned_properties():
    mock = Mock()
    mock.five = 5

    assert mock.five == 5


def test_mock_records_calls():
    with Mock() as mock:
        mock.get_five().returns(5)

    assert mock.get_five() == 5
