import pytest
from unittest.mock import Mock
from mockitup import allow, ANY_ARGS
from hamcrest import any_of


def basic_wildcards_example():
    picky_eater = Mock()

    allow(picky_eater).eat(any_of("pizza", "hamburger")).returns("yum")
    allow(picky_eater).eat(ANY_ARGS).raises(ValueError())

    assert picky_eater.eat("pizza") == "yum"
    assert picky_eater.eat("hamburger") == "yum"

    with pytest.raises(ValueError):
        picky_eater.eat("vegetables")

    with pytest.raises(ValueError):
        picky_eater.eat("fruits")
