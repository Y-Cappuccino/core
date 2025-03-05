import asyncio

import pytest
import pytest_asyncio

from ycappuccino.core.framework import YCappuccino
from ycappuccino.core.repositories.component_repositories import (
    InMemoryYComponentRepository,
)
from ycappuccino.core.services.component_discovery import FileComponentDiscovery
from ycappuccino.core.services.component_loader import FileComponentLoader
from ycappuccino.core.services.component_runner import FakeComponentRunner


@pytest.mark.asyncio
class TestFramework(object):

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.component_repository = InMemoryYComponentRepository()
        self.component_loader = FileComponentLoader()
        self.component_discovery = FileComponentDiscovery()
        self.framework = YCappuccino(
            FakeComponentRunner(
                self.component_repository,
                self.component_loader,
                self.component_discovery,
            )
        )

    async def test_start(self) -> None:
        self.framework.start()
        await asyncio.sleep(0.1)
        assert len(await self.component_repository.list()) == 19
        assert len(self.component_loader.generated_components) == 6
