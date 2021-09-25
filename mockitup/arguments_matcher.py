from collections import namedtuple
from typing import Any, Mapping, Tuple

import hamcrest
from hamcrest import match_equality
from hamcrest.core.matcher import Matcher

ANY_ARG = object()
ANY_ARGS = object()


class ArgumentsMatcher(namedtuple("StrictArgs", ["args", "kwargs"])):

    def matches(self, args: Tuple[Any], kwargs: Mapping[str, Any]) -> "ArgumentsMatchResult":
        matched, explanation = self._matches(args, kwargs)
        return ArgumentsMatchResult(matched, explanation)

    def _matches(self, args: Tuple[Any], kwargs: Mapping[str, Any]) -> Tuple[bool, str]:
        registered_len = len(self.args) + len(self.kwargs)
        provided_len = len(args) + len(kwargs)
        if registered_len == provided_len == 0:
            return True, "Arguments matched"

        if registered_len != provided_len:
            return False, "Length of provided positional arguments isn't the same as the registered"

        if self.args[0] is ANY_ARGS:
            return True, "Matched wildcard `ANY_ARGS`"

        for index, (registered, provided) in enumerate(zip(self.args, args)):
            matched = self.__match_values(registered, provided)
            if not matched:
                return False, (f"Positional arguments at index {index} didn't match "
                               f"(registered: `{registered}`, provided: `{provided}`)")

        # Should have same keys
        if set(self.kwargs) != set(kwargs):
            return False, "Length of provided named arguments isn't the same as the registered"

        for key in self.kwargs:
            registered = self.kwargs[key]
            provided = kwargs[key]
            if not self.__match_values(registered, provided):
                return False, (f"Named arguments at key `{key}` didn't match "
                               f"(registered: `{registered}`, provided: `{provided}`)")
        return True, "Arguments matched"

    @staticmethod
    def __match_values(registered_value: Any, provided_value: Any) -> bool:
        if registered_value is ANY_ARG:
            return True

        if isinstance(registered_value, Matcher):
            registered_value = match_equality(registered_value)

        return bool(registered_value == provided_value)


class ArgumentsMatchResult:

    def __init__(self, succeeded: bool, explanation: str):
        self.__succeeded = succeeded
        self.__explanation = explanation

    def __bool__(self) -> bool:
        return self.__succeeded

    @property
    def explanation(self) -> str:
        return self.__explanation

    def raise_for_failure(self) -> None:
        if not self:
            raise ArgumentsNotMatchedError(self.explanation)


class ArgumentsNotMatchedError(Exception):
    pass
