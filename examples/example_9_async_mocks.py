from unittest.mock import AsyncMock

import pytest
from mockitup import allow, expectation_suite


@pytest.mark.anyio
async def fine_support_for_async_mocks():
    amock = AsyncMock()

    allow(amock).get().returns("fun")

    assert await amock.get() == "fun"


@pytest.mark.anyio
async def works_with_expectations_as_well_example():
    with expectation_suite() as es:
        amock = AsyncMock()
        es.expect(amock).do_thing().returns("very fun")

        assert await amock.do_thing()


@pytest.mark.anyio
async def async_generators_example():
    amock = AsyncMock()

    allow(amock).aiter().yields_from([1, 2, 3, 4])

    result = [x async for x in amock.aiter()]
    assert result == [1, 2, 3, 4, 5]