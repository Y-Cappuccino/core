import os

import pytest

from ycappuccino.api.core import YCappuccino
from ycappuccino.core.adapters.component_discovery import FileComponentDiscovery
from ycappuccino.core.adapters.fake_bundle_context import (
    FakeBundleContext,
    FakeModuleType,
)
from ycappuccino.core import framework
from ycappuccino.core.api import ComponentDiscovered


@pytest.mark.asyncio
class TestComponentDiscovery(object):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.discovery = FileComponentDiscovery()
        self.discovery.path = os.getcwd() + "/test_component_discovery"
        self.discovery.context = FakeBundleContext()
        self.framework = framework.get_framework()
        self.framework.bundle_prefix = ["ycappuccino"]

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
    async def test_given_path_when_discover_then_component_discovered(
        self, component_discovered
    ):
        # Given
        await self.discovery.discover(self.discovery.path)
        # When
        assert len(self.framework.component_repository.components) == 3
        for component_assert in component_discovered:
            # then
            component_discovered = await self.framework.component_repository.get(
                component_assert.module_name
            )
            assert component_discovered.module_name == component_assert.module_name
            assert (
                component_discovered.module.__name__ == component_assert.module.__name__
            )
            assert component_discovered.path == component_assert.path.replace(
                os.sep, "/"
            )
