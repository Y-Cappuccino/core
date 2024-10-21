import json
import os
from pathlib import Path

import pytest
import typing as t
from ycappuccino.core.adapters.inspect_module import (
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
            os.getcwd() + "/../../main/python/ycappuccino/core/services/base"
        )
        self.discovery.context = FakeBundleContext()
        self.discovery._inspect_module = InspectModuleType()
        self.framework = framework.get_framework()
        self.framework.bundle_prefix = ["ycappuccino"]

    @pytest.mark.parametrize(
        ("components_discovered", "ycappuccino_components"),
        [
            (
                [
                    ComponentDiscovered(
                        module_name="list_components",
                        module=FakeModuleType("list_components"),
                        path=os.getcwd() + "/list_components.py",
                    ),
                    ComponentDiscovered(
                        module_name="activity_logger",
                        module=FakeModuleType("activity_logger"),
                        path=os.getcwd() + "/activity_logger.py",
                    ),
                    ComponentDiscovered(
                        module_name="configuration",
                        module=FakeModuleType("configuration"),
                        path=os.getcwd() + "/configuration.py",
                    ),
                ],
                "dict_values([<class 'configuration.Configuration'>, <class 'activity_logger.ActivityLogger'>, <class 'list_components.ListComponent'>])",
            ),
        ],
    )
    async def test_given_path_when_discover_then_component_discovered(
        self,
        components_discovered: t.List[ComponentDiscovered],
        ycappuccino_components: str,
    ):
        # Given
        await self.discovery.discover(self.discovery.path)
        # When
        assert len(self.framework.component_repository.components) == 4
        for component_assert in components_discovered:
            # then
            component_discovered = await self.framework.component_repository.get(
                component_assert.module_name
            )
            assert component_discovered.module_name == component_assert.module_name
            assert (
                component_discovered.module.__name__ == component_assert.module.__name__
            )
            path = Path(component_discovered.path)
            expect_path = Path(component_assert.path)
            assert path.cwd() == expect_path.cwd()

        assert (
            self.framework.component_repository.ycappuccino_classes.values().__str__()
            == ycappuccino_components
        )
