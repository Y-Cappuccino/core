import abc
import asyncio
import glob
import os

import typing as t
from pelix.ipopo.decorators import (
    ComponentFactory,
    Requires,
    Validate,
    Provides,
    Instantiate,
    Invalidate,
)
from pelix.framework import BundleContext

from ycappuccino.api.core import (
    ComponentDiscovered,
    IComponentDiscovery,
    IInspectModule,
)
from ycappuccino.core import framework


class ComponentDiscovery(abc.ABC, IComponentDiscovery):

    @abc.abstractmethod
    def discover(self, path: str) -> None: ...


@ComponentFactory("FileComponentDiscovery-Factory")
@Provides(specifications=[IComponentDiscovery.__name__])
@Requires("_inspect_module", IInspectModule.__name__)
@Instantiate("FileComponentDiscovery")
class FileComponentDiscovery(ComponentDiscovery):
    """
    browser file to discover component
    """

    def __init__(self):
        self.path: t.Optional[str] = None
        self.context: t.Optional[BundleContext] = None
        self._inspect_module: t.Optional[IInspectModule] = None

    @Validate
    def validate(self, a_context: BundleContext) -> None:
        self.context = a_context
        self.path = (
            framework.get_framework().application_yaml["component_path"]
            if framework.get_framework().application_yaml is not None
            and "component_path" in framework.get_framework().application_yaml.keys()
            else os.getcwd() + "/../"
        )
        asyncio.run(self.discover(self.path))

    @Invalidate
    def in_validate(self, a_context: BundleContext) -> None:
        self.context = None

    async def discover(self, path: str) -> None:
        """
        discover component in path
        :param path:
        :return:
        """
        await self._discover(path)
        for comp in framework.get_framework().component_repository.components.values():
            for klass in self._inspect_module.get_ycappuccino_component(comp.module):
                await framework.get_framework().component_repository.add_type(klass)

    async def _discover(self, path: str, module_name: t.Optional[str] = "") -> None:
        """
        discover component in path
        :param path:
        :param module_name:
        :return:
        """
        for file in glob.iglob(path + "/*"):
            file = file.replace(os.sep, "/")
            if "/" in file and not file.split("/")[-1].startswith("test_"):

                if (
                    os.path.exists(file)
                    and "pelix" not in file
                    and "pelix" not in module_name
                    and "framework" not in file
                ):
                    w_module_name = ""

                    if os.path.isdir(file) and os.path.isfile(file + "/__init__.py"):
                        if module_name == "":
                            w_module_name = (
                                file.split("/")[-2] + "." + file.split("/")[-1]
                            )

                        else:
                            w_module_name = module_name + "." + file.split("/")[-1]
                        await self._discover(
                            file,
                            w_module_name,
                        )
                    elif os.path.isfile(file) and file.endswith(".py"):
                        if module_name == "":
                            w_module_name = file.split("/")[-1][:-3]
                        else:
                            w_module_name = module_name + "." + file.split("/")[-1][:-3]
                        # yield ComponentDiscovered(
                        installed_bundle = self.context.install_bundle(
                            w_module_name, file
                        )
                        installed_bundle.start()
                        module = installed_bundle.get_module()

                        await framework.get_framework().component_repository.upsert(
                            ComponentDiscovered(
                                module=module,
                                path=file,
                                module_name=w_module_name,
                            )
                        )

                    else:
                        await self._discover(
                            file,
                            w_module_name,
                        )
