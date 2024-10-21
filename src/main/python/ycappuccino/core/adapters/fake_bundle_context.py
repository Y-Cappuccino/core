import importlib.util
from types import ModuleType
from pelix.framework import BundleContext, Bundle


class FakeModuleType(ModuleType):

    def __init__(self, name: str):
        self.__name__ = name


class FakeBundle(Bundle):

    def __init__(self, module_name: str, file: str):
        self.module_name = module_name
        self.file = file
        self.module_type = None

    def start(self):
        if self.file is not None:
            spec = importlib.util.spec_from_file_location(self.module_name, self.file)
            self.module_type = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module_type)

    def get_module(self) -> ModuleType:
        return self.module_type


class FakeBundleContext(BundleContext):

    def __init__(self, *args, **kwargs):
        pass

    def install_bundle(self, module_name: str, file: str = None) -> Bundle:
        return FakeBundle(module_name, file)
