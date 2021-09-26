from unittest.mock import Mock

from mockitup import allow


def can_return_multiple_values_seperately_example():
    mock = Mock()
    allow(mock).get().returns(1, 2, 3)

    assert mock.get() == 1
    assert mock.get() == 2
    assert mock.get() == 3

    # If all return values are exhausted, keeps returning the last one.
    assert mock.get() == 3
    assert mock.get() == 3
