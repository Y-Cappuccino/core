# core
import abc
import inspect
from types import ModuleType

from pelix.ipopo.decorators import ComponentFactory, Instantiate, Provides

from ycappuccino.api.core import IInspectModule, YCappuccinoComponent


class InspectModule(abc.ABC, IInspectModule):
    @abc.abstractmethod
    def get_ycappuccino_component(self, module: ModuleType) -> list[type]:
        pass

    def is_ycappuccino_component(
        self, a_klass: type, include_pelix: bool = False
    ) -> bool:
        first = True
        for supertype in inspect.getmro(a_klass):
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


import typing as t


class FakeInspectModuleType(InspectModule):

    def __init__(self, ycappuccino_by_module: t.Dict[str, t.List[type]]):
        self.ycappuccino_by_module = ycappuccino_by_module

    def get_ycappuccino_component(self, module: ModuleType) -> list[type]:
        list: t.List[type] = []
        for name in self.ycappuccino_by_module.keys():
            if name in module.__name__:
                list.extend(self.ycappuccino_by_module[name])
        return list

    def add_ycappuccino_component(self, module_name: str, klass: type):
        if module_name not in self.ycappuccino_by_module:
            self.ycappuccino_by_module[module_name] = []
        self.ycappuccino_by_module[module_name].append(klass)


@ComponentFactory("InspectModule-Factory")
@Provides(specifications=[IInspectModule.__name__])
@Instantiate("InspectModule")
class InspectModuleType(InspectModule):

    def get_ycappuccino_component(self, module: ModuleType) -> list[type]:
        list_klass: list[type] = [
            klass
            for name, klass in inspect.getmembers(module, inspect.isclass)
            if inspect.isclass(klass)
        ]
        # get  class is YCappuccinoComponent
        list_ycappuccino_component: list[type] = [
            klass for klass in list_klass if self.is_ycappuccino_component(klass)
        ]
        return list_ycappuccino_component
