import abc
from typing import Iterator
import typing as t
from ycappuccino.core.adapters.component_discovery import ComponentDiscovered


class IComponentRepository:
    async def get(self, module_name: str) -> ComponentDiscovered: ...
    async def upsert(self, component: ComponentDiscovered) -> None: ...
    async def delete(self, module_name) -> ComponentDiscovered: ...
    async def clear(self) -> None: ...
    async def list(self) -> t.List[ComponentDiscovered]: ...


class YComponentRepository(abc.ABC, IComponentRepository):

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


class InMemoryYComponentRepository(YComponentRepository):
    """
    In memory repository for component discovered
    """

    def __init__(self):
        self.components: t.Dict[str, ComponentDiscovered] = {}

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
