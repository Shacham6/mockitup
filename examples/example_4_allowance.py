from unittest.mock import Mock

from mockitup import allow


def use_allow_for_simple_cases_example():
    mock = Mock()
    allow(mock).get_five().returns(5)

    assert mock.get_five() == 5
