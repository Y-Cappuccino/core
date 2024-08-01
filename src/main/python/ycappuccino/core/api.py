import dataclasses
from types import ModuleType
import typing as t


@dataclasses.dataclass
class ComponentDiscovered:

    module: ModuleType
    module_name: str
    path: t.Optional[str] = None
    ycappuccino_classes: t.Optional[t.List[type]] = None


@dataclasses.dataclass
class GeneratedComponent:
    module_name: str
    content: str


class IYCappuccinoComponentLoader:
    def generate(self, component_discovered: ComponentDiscovered) -> ModuleType: ...
    def load(self, component_discovered: ComponentDiscovered) -> ModuleType: ...
    def loads(self) -> ModuleType: ...


class IComponentDiscovery:

    def discover(
        self, path: str, module_name: t.Optional[str] = None
    ) -> t.AsyncIterator[ComponentDiscovered]:
        pass
