import os

import pytest

from ycappuccino.core.adapters.inspect_module import (
    FakeInspectModuleType,
    InspectModuleType,
)
from ycappuccino.core.services.component_discovery import FileComponentDiscovery
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
        self.discovery.path = (
            os.getcwd() + "../../main/python/ycappuccino/core/service/base"
        )
        self.discovery.context = FakeBundleContext()
        self.discovery._inspect_module = InspectModuleType()
        self.framework = framework.get_framework()
        self.framework.bundle_prefix = ["ycappuccino"]

    @pytest.mark.parametrize(
        "component_discovered",
        [
            [
                ComponentDiscovered(
                    module_name="list_components",
                    module=FakeModuleType("list_components"),
                    path=os.getcwd() + "/list_components.py",
                    ycappuccino_classes=[],
                ),
                ComponentDiscovered(
                    module_name="activity_logger",
                    module=FakeModuleType("activity_logger"),
                    path=os.getcwd() + "/activity_logger.py",
                    ycappuccino_classes=[],
                ),
                ComponentDiscovered(
                    module_name="configuration",
                    module=FakeModuleType("configuration"),
                    path=os.getcwd() + "/configuration.py",
                    ycappuccino_classes=[],
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
            assert (
                component_discovered.ycappuccino_classes
                == component_assert.ycappuccino_classes
            )
