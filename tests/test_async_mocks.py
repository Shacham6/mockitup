from unittest.mock import AsyncMock

import pytest
from mockitup import allow, expectation_suite


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
