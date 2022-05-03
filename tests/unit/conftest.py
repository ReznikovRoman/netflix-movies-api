from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from src.main import app

from .testlib import APIClient


if TYPE_CHECKING:
    from asyncio import AbstractEventLoop


pytestmark = [pytest.mark.asyncio]


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def client() -> APIClient:
    async with APIClient(app=app, base_url="http://test") as ac:
        yield ac
