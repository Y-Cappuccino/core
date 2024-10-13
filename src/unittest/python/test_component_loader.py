import os

import pytest, pytest_asyncio

from ycappuccino.core.adapters.fake_bundle_context import (
    FakeBundleContext,
    FakeModuleType,
)
from ycappuccino.core import framework
from ycappuccino.core.adapters.inspect_module import FakeInspectModuleType
from ycappuccino.core.api import ComponentDiscovered, GeneratedComponent

import typing as t

from ycappuccino.core.services.base.activity_logger import ActivityLogger
from ycappuccino.core.services.base.configuration import Configuration
from ycappuccino.core.services.base.list_components import ListComponent
from ycappuccino.core.services.component_loader import FileComponentLoader


@pytest.mark.asyncio
class TestComponentDiscovery(object):

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.discovered_components: t.List[ComponentDiscovered] = [
            ComponentDiscovered(
                module_name="list_components",
                module=FakeModuleType("list_components"),
                path=os.getcwd()
                + "/../../main/python/ycappuccino/core/services/base/list_components.py",
            ),
            ComponentDiscovered(
                module_name="activity_logger",
                module=FakeModuleType("activity_logger"),
                path=os.getcwd()
                + "/../../main/python/ycappuccino/core/services/base/activity_logger.py",
            ),
            ComponentDiscovered(
                module_name="configuration",
                module=FakeModuleType("configuration"),
                path=os.getcwd()
                + "/../../main/python/ycappuccino/core/services/base/configuration.py",
            ),
        ]
        self.component_loader: FileComponentLoader = FileComponentLoader()
        self.bundle_context = FakeBundleContext()
        self.component_loader._inspect_module = FakeInspectModuleType(
            ycappuccino_by_module={
                "list_components": [ListComponent],
                "activity_logger": [ActivityLogger],
                "configuration": [Configuration],
            }
        )

        self.component_loader.context = self.bundle_context

        self.framework = framework.get_framework()
        for comp_discovered in self.discovered_components:
            await framework.get_framework().component_repository.upsert(comp_discovered)
        for (
            klasses
        ) in self.component_loader._inspect_module.ycappuccino_by_module.values():
            for klass in klasses:
                await framework.get_framework().component_repository.add_type(klass)

        self.framework.bundle_prefix = ["ycappuccino"]

    @staticmethod
    def read_generated_file(name_path: str) -> str:
        content = ""
        with open(os.getcwd() + f"/generated_component/{name_path}.txt", "r") as file:
            content = "".join(file.readlines())
        return content

    @pytest.mark.parametrize(
        "generate_components",
        [
            [
                GeneratedComponent(
                    module_name="list_components_pelix",
                    content=read_generated_file("list_components_pelix"),
                ),
                GeneratedComponent(
                    module_name="activity_logger_pelix",
                    content=read_generated_file("activity_logger_pelix"),
                ),
                GeneratedComponent(
                    module_name="configuration_pelix",
                    content=read_generated_file("configuration_pelix"),
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
