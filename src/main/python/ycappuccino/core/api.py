import dataclasses
from types import ModuleType
import typing as t


@dataclasses.dataclass
class ComponentDiscovered:

    module: ModuleType
    module_name: str
    path: t.Optional[str] = None


@dataclasses.dataclass
class GeneratedComponent:
    module_name: str
    content: str


class IYCappuccinoComponentLoader:
    def generate(self, component_discovered: ComponentDiscovered) -> ModuleType: ...
    def load(self, component_discovered: ComponentDiscovered) -> ModuleType: ...
    def loads(self) -> ModuleType: ...


class IComponentDiscovery:

    def discover(self, path: str) -> None: ...


class IInspectModule:

    def get_ycappuccino_component(self, module: ModuleType) -> list[type]: ...

    def is_ycappuccino_component(
        self, a_klass: type, include_pelix: bool = False
    ) -> bool: ...
