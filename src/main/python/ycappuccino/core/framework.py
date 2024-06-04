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


def is_ycappuccino_component(a_klass: type, include_pelix: bool = False) -> bool:
    first = True
    for supertype in a_klass.__mro__:
        if supertype is not inspect._empty:
            if supertype.__name__ == YCappuccinoComponent.__name__:
                if first:
                    return False
                else:
                    return True
            elif include_pelix and a_klass is not inspect._empty:
                list_subclass = supertype.__subclasses__()
                for subclass in list_subclass:
                    if hasattr(subclass, "_ipopo_property_getter"):
                        return True

        first = False
    return False


def get_ycappuccino_component(module: ModuleType) -> list[type]:
    list_klass: list[type] = [
        klass
        for name, klass in inspect.getmembers(module, inspect.isclass)
        if inspect.isclass(klass)
    ]
    # get  class is YCappuccinoComponent
    list_ycappuccino_component: list[type] = [
        klass for klass in list_klass if framework.is_ycappuccino_component(klass)
    ]
    return list_ycappuccino_component


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
        self.bundle_prefix = None

    def get_bundle_prefix(self):

        if self.bundle_prefix is None:
            self.bundle_prefix = None
            if "bundle_prefix" in self.application_yaml.keys():
                self.bundle_prefix = self.application_yaml["bundle_prefix"]
        return [self.bundle_prefix]

    def start(self, yml_path: str) -> None:
        """initiate ipopo runtime and handle component that auto discover bundle and ycappuccino component"""
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
            )
        )

        # Start the framework
        self.ipopo.start()
        # Instantiate EventAdmin
        with use_ipopo(self.ipopo.get_bundle_context()) as ipopo:
            ipopo.instantiate(
                pelix.services.FACTORY_EVENT_ADMIN, "event-client_pyscript_core", {}
            )

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
