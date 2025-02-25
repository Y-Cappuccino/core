import abc
import inspect
import sys
from types import ModuleType
import typing as t
import pelix
import yaml
from ycappuccino.api.core import IFramework, YCappuccinoComponent
from pelix.framework import BundleContext, create_framework
from pelix.ipopo.constants import use_ipopo  # type: ignore
import pelix.services  # type: ignore
from ycappuccino.core.repositories.component_repositories import (
    InMemoryYComponentRepository,
)

framework = None


def get_framework():
    global framework

    if framework is None:
        framework = YCappuccino()

    return framework


class Framework(abc.ABC, IFramework):

    def __init__(self):
        self.component_repository = InMemoryYComponentRepository()

    def get_component_repository(self):
        return self.component_repository

    @abc.abstractmethod
    def start(self, yml_path: str) -> None:
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        pass


class YCappuccino(Framework):

    def __init__(
        self,
    ):
        super().__init__()
        self.application_yaml = None
        self.bundle_prefix = None

    def get_bundle_prefix(self):

        if self.bundle_prefix is None:
            self.bundle_prefix = None
            if "bundle_prefix" in self.application_yaml.keys():
                self.bundle_prefix = self.application_yaml["bundle_prefix"]
        return [self.bundle_prefix]

    def start(self, yml_path: str) -> None:
        """initiate ipopo runtime and handle component that auto discover bundle and ycappuccino component"""
        if yml_path is not None:
            with open(yml_path, "r") as file:
                self.application_yaml = yaml.safe_load(file)
        self.ipopo: t.Optional[pelix.framework.Framework] = None
        self.context: t.Optional[BundleContext] = None

        # Create the Pelix framework
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
            )
        )

        # Start the framework
        self.ipopo.start()
        # Instantiate EventAdmin
        with use_ipopo(self.ipopo.get_bundle_context()) as ipopo:
            ipopo.instantiate(
                pelix.services.FACTORY_EVENT_ADMIN, "event-client_pyscript_core", {}
            )
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

    def stop(self) -> None:
        pass
