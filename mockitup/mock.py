from typing import Any

from .attr_proxy import MethProxy
from unittest import mock


class _MockMembers(mock.MagicMixin):

    def __init__(self):
        self.recording = False
        self.function_calls = {}
        self.properties = {}


class Mock:

    def __init__(self):
        self._mock_members = _MockMembers()
        self.__setattr__ = self.__mock_setattr__

    def __getattr__(self, attr: str):
        members = _mock_members(self)
        if not members.recording:
            raise ValueError()

        if attr in members.properties:
            return members.properties[attr]

        return MethProxy(attr, None)

    def __mock_setattr__(self, attr: str, value: Any):
        if _mock_members(self).recording:
            _mock_members(self).properties[attr] = value
            return
        object.__setattr__(self, attr, value)

    def __enter__(self):
        _mock_members(self).recording = True
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        _mock_members(self).recording = False


def _mock_members(mock) -> _MockMembers:
    return object.__getattribute__(mock, "_mock_members")
