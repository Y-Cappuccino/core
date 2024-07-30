import os

import pytest

from ycappuccino.api.core import YCappuccino
from ycappuccino.core.adapters.component_discovery import FileComponentDiscovery
from ycappuccino.core.adapters.fake_bundle_context import (
    FakeBundleContext,
    FakeModuleType,
)
from ycappuccino.core import framework
from ycappuccino.core.api import ComponentDiscovered, GeneratedComponent

import typing as t

from ycappuccino.core.services.component_loader import FileComponentLoader


@pytest.mark.asyncio
class TestComponentDiscovery(object):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.discovered_components: t.List[ComponentDiscovered] = [
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
        self.component_loader: FileComponentLoader = FileComponentLoader()
        self.bundle_context = FakeBundleContext()

        self.component_loader.context = self.bundle_context

        self.framework = framework.get_framework()
        self.framework.bundle_prefix = ["ycappuccino"]

    @pytest.mark.parametrize(
        "generate_component",
        [
            [
                GeneratedComponent(
                    module_name="list_components",
                    content="content",
                ),
                GeneratedComponent(
                    module_name="activity_logger",
                    content="content",
                ),
                GeneratedComponent(
                    module_name="configuration",
                    content="content",
                ),
            ]
        ],
    )
    async def test_given_discovered_component_when_generate_then_generated_module_done(
        self,
    ):
        # Given
        # When
        generate_component = await self.component_loader.generate(
            self.discovered_components[0]
        )
        generate_component = await self.component_loader.generate(
            self.discovered_components[1]
        )
        generate_component = await self.component_loader.generate(
            self.discovered_components[2]
        )
        # then
