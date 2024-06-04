import sys
from types import ModuleType
from pelix.framework import BundleContext, Bundle


class FakeModuleType(ModuleType):

    def __init__(self, name: str):
        self.__name__ = name


class FakeBundle(Bundle):

    def __init__(self, module_name: str, file: str):
        self.module_name = module_name
        self.file = file

    def start(self):
        pass

    def get_module(self) -> ModuleType:
        return FakeModuleType(self.module_name)


class FakeBundleContext(BundleContext):

    def __init__(self, *args, **kwargs):
        pass

    def install_bundle(self, module_name: str, file: str) -> Bundle:
        return FakeBundle(module_name, file)
