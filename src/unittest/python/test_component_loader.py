import os

import pytest

from ycappuccino.core.adapters.component_discovery import FileComponentDiscovery
from ycappuccino.core.adapters.fake_bundle_context import (
    FakeModuleType,
    FakeBundleContext,
)
from ycappuccino.core.api import ComponentDiscovered
from ycappuccino.core import framework
from ycappuccino.core.services.component_loader import YCappuccinoComponentLoaderImpl


@pytest.mark.asyncio
class TestComponentLoader:

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.framework = framework.get_framework()

        self.discovery = FileComponentDiscovery()
        self.loader = YCappuccinoComponentLoaderImpl()

        self.discovery.path = os.getcwd() + "/test_component_discovery"
        self.discovery.context = FakeBundleContext()
        self.framework.bundle_prefix = ["ycappuccino"]

        self.loader.context = self.discovery.context
        self.loader.component_discovery = self.discovery

    @pytest.mark.parametrize(
        "component_discovered",
        [
            [
                ComponentDiscovered(
                    module_name="list_components",
                    module=FakeModuleType("list_components"),
                    path=os.getcwd() + "/test_component_discovery/list_components.py",
                ),
                ComponentDiscovered(
                    module_name="activity_logger",
                    module=FakeModuleType("activity_logger"),
                    path=os.getcwd() + "/test_component_discovery/activity_logger.py",
                ),
                ComponentDiscovered(
                    module_name="configuration",
                    module=FakeModuleType("configuration"),
                    path=os.getcwd() + "/test_component_discovery/configuration.py",
                ),
            ]
        ],
    )
    async def test_given_component_discovered_when_load_then_component_loaded_then_component_loaded(
        self, component_discovered: ComponentDiscovered
    ) -> None:
        await self.discovery.discover(self.discovery.path)
        await self.loader.loads()
        assert len(self.framework.component_repository.components) == 3
        assert len(self.loader.list_bundles) == 6

    def test_given_loaded_component_discovered_when_generate_component_then_component_generated(
        self,
    ) -> None:
        pass

    def test_given_generated_component_when_load_generated_component_then_component_loaded(
        self,
    ) -> None:
        pass
