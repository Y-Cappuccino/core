import abc
import sys
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
from ycappuccino.core.services.component_runner import (
    IComponentRunner,
    PelixComponentRunner,
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
        component_runner: IComponentRunner = PelixComponentRunner(),
    ):
        super().__init__()
        self.application_yaml = None
        self.bundle_prefix = None
        self.component_runner = component_runner

    def start(self, yml_path: str) -> None:
        """initiate ipopo runtime and handle component that auto discover bundle and ycappuccino component"""
        if yml_path is not None:
            with open(yml_path, "r") as file:
                self.application_yaml = yaml.safe_load(file)
        self.component_runner.set_config(self.application_yaml)

        self.component_runner.run()

    def stop(self) -> None:
        pass
