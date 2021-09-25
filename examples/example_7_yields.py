from unittest.mock import Mock

from mockitup import expectation_suite


def iterating_mock_example():
    with expectation_suite() as es:
        mock = Mock()
        es.expect(mock).iter_numbers().yields_from([1, 2, 3, 4])

        result = mock.iter_numbers()
        assert not isinstance(result, list)
        assert list(result) == [1, 2, 3, 4]
