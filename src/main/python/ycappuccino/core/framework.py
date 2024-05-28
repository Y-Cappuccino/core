import abc
from typing import Optional

from ycappuccino.api.core import IFramework
from pelix.framework import BundleContext

framework = None


def get_framework():
    global framework

    if framework is None:
        framework = YCappuccino()

    return framework


class Framework(abc.ABC, IFramework):

    def __init__(self):
        pass

    @abc.abstractmethod
    def start(self) -> None:
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        pass


class YCappuccino(Framework):

    def __init__(self):
        pass

    def start(self) -> None:
        """initiate ipopo runtime and handle component that auto discover bundle and ycappuccino component"""
        pass

    def stop(self) -> None:
        pass
