# core
import os
import sys
import time

import pelix.services
from pelix.framework import BundleContext, create_framework
from pelix.ipopo.constants import use_ipopo
import typing as t
from ycappuccino.api.core import IComponentDiscovery, IComponentLoader, IComponentRunner
from ycappuccino.core.adapters import inspect_module
from ycappuccino.core.adapters.fake_bundle_context import FakeBundleContext
from ycappuccino.core.adapters.inspect_module import (
    FakeInspectModuleType,
    InspectModuleType,
)
from ycappuccino.core.repositories.component_repositories import (
    IComponentRepository,
)
from ycappuccino.core.services import component_discovery, component_loader
from ycappuccino.core.services.base.activity_logger import ActivityLogger
from ycappuccino.core.services.base.configuration import Configuration
from ycappuccino.core.services.base.list_components import ListComponent

path_module = os.path.dirname(__file__)


class FakeComponentRunner(IComponentRunner):

    def __init__(
        self,
        component_repository: IComponentRepository,
        component_loader: IComponentLoader,
        component_discovery: IComponentDiscovery,
    ) -> None:
        super().__init__()
        self.component_repositories = component_repository
        self.component_loader = component_loader
        self.component_loader._component_repository = self.component_repositories
        bundle_context = FakeBundleContext()
        self.component_loader._inspect_module = FakeInspectModuleType(
            ycappuccino_by_module={
                "list_components": [ListComponent],
                "activity_logger": [ActivityLogger],
                "configuration": [Configuration],
            }
        )

        self.component_loader.context = bundle_context
        self.component_discovery = component_discovery
        self.component_discovery._component_repository = self.component_repositories
        self.component_discovery.path = (
            path_module + "/../../../main/python/ycappuccino/core/services/base"
        )
        self.component_discovery.context = FakeBundleContext()
        self.component_discovery._inspect_module = InspectModuleType()

    def set_config(self, a_config: t.Dict[str, t.Any]) -> t.List[str]:
        return []

    async def run(self):
        # execute what will framework do to discover and load component
        self.component_discovery.validate(self.component_discovery.context)  # type: ignore
        time.sleep(0.1)
        self.component_loader.validate(self.component_loader.context)  # type: ignore
        time.sleep(0.1)


class PelixComponentRunner(IComponentRunner):

    def __init__(
        self,
    ):
        super().__init__()
        self.ipopo: t.Optional[pelix.framework.Framework] = None
        self.context: t.Optional[BundleContext] = None
        self.bundle_prefix: t.Optional[str] = None

    def set_config(self, a_config: t.Dict[str, t.Any]) -> t.List[str]:
        if a_config is not None:
            if self.bundle_prefix is None:
                self.bundle_prefix = None
                if "bundle_prefix" in a_config.keys():
                    self.bundle_prefix = a_config["bundle_prefix"]
            return [self.bundle_prefix]
        return []

    async def run(self):
        self.ipopo = create_framework(
            (
                # iPOPO
                "pelix.ipopo.core",
                # Shell ycappuccino_storage
                "pelix.shell.core",
                "pelix.shell.console",
                "pelix.shell.remote",
                "pelix.shell.ipopo",
                # ConfigurationAdmin
                "pelix.services.configadmin",
                "pelix.shell.configadmin",
                # EventAdmin,
                "pelix.services.eventadmin",
                "pelix.shell.eventadmin",
                "ycappuccino.core.services.component_discovery",
                "ycappuccino.core.services.component_loader",
                "ycappuccino.core.repositories.component_repositories",
                "ycappuccino.core.adapters.inspect_module",
                "ycappuccino.core.services.component_discovery",
            )
        )

        # Start the framework
        self.ipopo.start()
        # Instantiate EventAdmin
        with use_ipopo(self.ipopo.get_bundle_context()) as ipopo:
            ipopo.instantiate(
                pelix.services.FACTORY_EVENT_ADMIN, "event-client_pyscript_core", {}
            )

        for bundle_name, path in [
            (
                "ycappuccino.core.services.component_discovery",
                component_discovery.__file__,
            ),
            ("ycappuccino.core.services.component_loader", component_loader.__file__),
        ]:
            # Install the bundle
            bundle = self.ipopo.get_bundle_context().install_bundle(bundle_name, path)
            # Start the bundle
            bundle.start()

        # Instantiate ycappuccino core
        self.context = self.ipopo.get_bundle_context()

        try:
            self.ipopo.wait_for_stop()

            # Wait for the framework to stop
        except Exception as ex:
            print(ex)
            self.ipopo.stop()
            sys.exit(0)

        self.ipopo.start()
