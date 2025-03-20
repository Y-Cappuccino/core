# core
import sys

import pytest

from ycappuccino.core.services.component_discovery import ComponentDiscovered
from ycappuccino.core.repositories.component_repositories import (
    InMemoryYComponentRepository,
)


@pytest.mark.asyncio
class TestComponentDiscoveredRepository(object):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.repository = InMemoryYComponentRepository()

    async def test_given_empty_repository_when_upsert_component_then_component_is_inserted(
        self,
    ):
        # Given
        component = ComponentDiscovered(
            module=sys.modules[__name__], module_name="module_name", path="path"
        )
        # When
        await self.repository.upsert(component)
        # Then
        assert await self.repository.get("module_name") == component

    async def test_given_empty_repository_when_get_component_then_component_not_found(
        self,
    ):
        # Given
        # When
        with pytest.raises(KeyError):
            await self.repository.get("module_name")
        # Then

    async def test_given_empty_repository_when_delete_component_then_component_not_found(
        self,
    ):
        # Given
        # When
        with pytest.raises(KeyError):
            await self.repository.delete("module_name")

    async def test_given_repository_with_component_when_get_component_then_component_found(
        self,
    ):
        # Given
        component = ComponentDiscovered(
            module=sys.modules[__name__], module_name="module_name", path="path"
        )
        await self.repository.upsert(component)

        # Then
        assert await self.repository.get("module_name") == component
        assert len(self.repository.components) == 1

    async def test_given_repository_with_component_when_delete_component_then_component_is_deleted(
        self,
    ):
        # Given
        component = ComponentDiscovered(
            module=sys.modules[__name__], module_name="module_name", path="path"
        )
        await self.repository.upsert(component)
        # When
        await self.repository.delete("module_name")
        # Then
        with pytest.raises(KeyError):
            await self.repository.get("module_name")
        assert len(self.repository.components) == 0

    async def test_given_repository_with_component_when_upsert_component_then_component_is_updated(
        self,
    ):
        # Given
        component = ComponentDiscovered(
            module=sys.modules[__name__], module_name="module_name", path="path"
        )
        await self.repository.upsert(component)
        component = ComponentDiscovered(
            module=sys.modules[__name__], module_name="module_name", path="path2"
        )
        # When
        await self.repository.upsert(component)
        # Then
        assert await self.repository.get("module_name") == component
