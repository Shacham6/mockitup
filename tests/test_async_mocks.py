from asyncmock import AsyncMock

import pytest
from mockitup import allow, expectation_suite, ANY_ARG, ANY_ARGS


@pytest.mark.anyio
async def test_async_mock_works():
    amock = AsyncMock()
    allow(amock).__call__("a").returns("waited so long")

    assert await amock("a") == "waited so long"


@pytest.mark.anyio
async def test_expectations():
    with expectation_suite() as es:
        amock = AsyncMock()
        es.expect(amock).a.b().returns("lol")

        assert await amock.a.b() == "lol"


@pytest.mark.anyio
async def test_async_with_argument_matching():
    amock = AsyncMock()
    allow(amock).func(1).returns(1)
    allow(amock).func(1, 2).returns((1, 2))
    allow(amock).func("a").returns("a")
    allow(amock).func(ANY_ARG).returns("ANY_ARG")
    allow(amock).func(ANY_ARGS).returns("ANY_ARGS")

    assert await amock.func(1) == 1
    assert await amock.func(1, 2) == (1, 2)
    assert await amock.func("a") == "a"
    assert await amock.func("lol") == "ANY_ARG"
    assert await amock.func("a", "b", "c", "d") == "ANY_ARGS"
    assert await amock.func(arg1="a", arg2="b", arg3="c") == "ANY_ARGS"
