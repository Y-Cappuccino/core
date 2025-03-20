# core
import abc
import typing as t

from pelix.ipopo.decorators import ComponentFactory, Instantiate, Provides

from ycappuccino.api.core_models import ComponentDiscovered


class IComponentRepository:

    def __init__(self):
        self.ycappuccino_classes: t.Dict[str, type] = {}
        self.components: t.Dict[str, ComponentDiscovered] = {}

    async def add_type(self, a_klass: type) -> None: ...
    async def get(self, module_name: str) -> ComponentDiscovered: ...
    async def upsert(self, component: ComponentDiscovered) -> None: ...
    async def delete(self, module_name) -> ComponentDiscovered: ...
    async def clear(self) -> None: ...
    async def list(self) -> t.List[ComponentDiscovered]: ...


class YComponentRepository(abc.ABC, IComponentRepository):
    @abc.abstractmethod
    async def add_type(self, a_klass: type) -> None: ...

    @abc.abstractmethod
    async def get(self, module_name: str) -> ComponentDiscovered: ...
    @abc.abstractmethod
    async def upsert(self, component: ComponentDiscovered) -> None: ...
    @abc.abstractmethod
    async def delete(self, module_name) -> ComponentDiscovered: ...
    @abc.abstractmethod
    async def clear(self) -> None: ...
    @abc.abstractmethod
    async def list(self) -> t.List[ComponentDiscovered]: ...


@ComponentFactory("InMemoryYComponentRepository-Factory")
@Provides(specifications=[IComponentRepository.__name__])
@Instantiate("InMemoryYComponentRepository")
class InMemoryYComponentRepository(YComponentRepository):
    """
    In memory repository for component discovered
    """

    def __init__(self):
        super().__init__()

    async def add_type(self, a_klass: type) -> None:
        if (
            a_klass is not None
            and len(a_klass.__subclasses__()) == 0
            and a_klass not in self.ycappuccino_classes
        ):
            self.ycappuccino_classes[a_klass.get_hash()] = a_klass
        elif (
            len(a_klass.__subclasses__()) == 0
            and a_klass.get_hash() in self.ycappuccino_classes
        ):
            del self.ycappuccino_classes[a_klass.get_hash()]

    async def get(self, module_name: str) -> ComponentDiscovered:
        if module_name not in self.components:
            raise KeyError(f"module {module_name} not found")
        return self.components.get(module_name)

    async def upsert(self, component: ComponentDiscovered) -> None:
        self.components[component.module_name] = component

    async def clear(self) -> None:
        self.components.clear()

    async def delete(self, module_name) -> ComponentDiscovered:
        comp = self.components[module_name]
        del self.components[module_name]
        return comp

    async def list(self) -> t.List[ComponentDiscovered]:
        result = []
        for component in self.components.values():
            result.append(component)
        return result
