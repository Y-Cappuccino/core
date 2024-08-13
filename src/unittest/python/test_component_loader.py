import os

import pytest, pytest_asyncio

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

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.discovered_components: t.List[ComponentDiscovered] = [
            ComponentDiscovered(
                module_name="list_components",
                module=FakeModuleType("list_components"),
                path=os.getcwd() + "/test_component_discovery/list_components.py",
                ycappuccino_classes=[],  # TODO
            ),
            ComponentDiscovered(
                module_name="activity_logger",
                module=FakeModuleType("activity_logger"),
                path=os.getcwd() + "/test_component_discovery/activity_logger.py",
                ycappuccino_classes=[],  # TODO
            ),
            ComponentDiscovered(
                module_name="configuration",
                module=FakeModuleType("configuration"),
                path=os.getcwd() + "/test_component_discovery/configuration.py",
                ycappuccino_classes=[],  # TODO
            ),
        ]
        self.component_loader: FileComponentLoader = FileComponentLoader()
        self.bundle_context = FakeBundleContext()

        self.component_loader.context = self.bundle_context

        self.framework = framework.get_framework()
        for comp_discovered in self.discovered_components:
            await framework.get_framework().component_repository.upsert(comp_discovered)
        self.framework.bundle_prefix = ["ycappuccino"]

    @pytest.mark.parametrize(
        "generate_components",
        [
            [
                GeneratedComponent(
                    module_name="list_components_pelix",
                    content="content",
                ),
                GeneratedComponent(
                    module_name="activity_logger_pelix",
                    content="content",
                ),
                GeneratedComponent(
                    module_name="configuration_pelix",
                    content="content",
                ),
            ]
        ],
    )
    async def test_given_discovered_component_when_generate_then_generated_module_done(
        self,
        generate_components: GeneratedComponent,
    ):
        # Given
        # When
        generate_component = await self.component_loader.generate(
            self.discovered_components[0]
        )
        assert generate_component.module_name == generate_components[0].module_name
        assert generate_component.content == generate_components[0].content
        generate_component = await self.component_loader.generate(
            self.discovered_components[1]
        )
        assert generate_component.module_name == generate_components[0].module_name
        assert generate_component.content == generate_components[0].content
        generate_component = await self.component_loader.generate(
            self.discovered_components[2]
        )
        assert generate_component.module_name == generate_components[0].module_name
        assert generate_component.content == generate_components[0].content
        # then
