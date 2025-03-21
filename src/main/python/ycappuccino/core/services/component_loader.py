# core
#
# class that allow to generate from ycapuccino components pelix components in order to be loaded by the pelix framework
#
import abc
import asyncio
import sys
import typing as t
import re
from datetime import datetime
from pathlib import Path
from types import ModuleType

from ycappuccino.api.core import (
    IComponentDiscovery,
    IInspectModule,
    IComponentLoader,
)
from pelix.ipopo.decorators import (
    ComponentFactory,
    Requires,
    Validate,
    Provides,
    Instantiate,
    Invalidate,
)

from ycappuccino.api.core_models import ComponentDiscovered, GeneratedComponent
from ycappuccino.api.executor_service import execute_async_in_thread
from ycappuccino.core.repositories.component_repositories import IComponentRepository
from pelix.framework import Bundle, BundleContext
import inspect


class ComponentLoader(IComponentLoader):

    def __init__(self):
        self._component_discovery = None

    @abc.abstractmethod
    def get_arg_new(self, all: list[list]) -> list[str]: ...
    @abc.abstractmethod
    def generate(self, component_discovered: ComponentDiscovered) -> ModuleType: ...

    @abc.abstractmethod
    def load_discovered(
        self, component_discovered: ComponentDiscovered
    ) -> ModuleType: ...
    @abc.abstractmethod
    def load_generated(self, component_generated: GeneratedComponent) -> ModuleType: ...

    @abc.abstractmethod
    def loads(self) -> ModuleType: ...


@ComponentFactory("FileComponentLoader-Factory")
@Provides(specifications=[IComponentLoader.__name__], controller="controller")
@Requires("_component_discovery", IComponentDiscovery.__name__)
@Requires("_inspect_module", IInspectModule.__name__)
@Requires("_component_repository", IComponentRepository.__name__)
@Instantiate("FileComponentLoader")
class FileComponentLoader(ComponentLoader):
    """
    class that allow to generate from ycapuccino components pelix components in order to be loaded by the pelix framework
    """

    def __init__(self):
        super().__init__()
        self.validate_task = None
        self.generated_components: t.Dict[str, GeneratedComponent] = {}
        self.context: t.Optional[BundleContext] = None
        self._component_discovery: t.Optional[IComponentDiscovery] = None
        self._component_repository: t.Optional[IComponentRepository] = None
        self.list_bundles: t.List[Bundle] = []
        self._inspect_module: t.Optional[IInspectModule] = None
        self.controller = False

    @Validate
    def validate(self, a_context: BundleContext) -> None:
        self.context = a_context

        execute_async_in_thread(self.loads)

    @Invalidate
    def in_validate(self, a_context: BundleContext) -> None:
        self.context = None

    async def generate(
        self, component_discovered: ComponentDiscovered
    ) -> t.List[GeneratedComponent]:
        res: t.List[GeneratedComponent] = []
        module_name = component_discovered.module_name
        module = component_discovered.module
        path = component_discovered.path
        pelix_module_father = ".".join(module_name.split(".")[:-1])

        if pelix_module_father == "":
            pelix_module_name = module_name.split(".")[-1] + "_pelix"
        else:
            pelix_module_name = (
                pelix_module_father + "." + module_name.split(".")[-1] + "_pelix"
            )

        # get  class is YCappuccinoComponent
        list_ycappuccino_component = self._inspect_module.get_ycappuccino_component(
            module
        )
        if not Path(path).exists():
            raise FileNotFoundError(f"file {path} not found")
        with open(path, "r") as f:
            content_original_file = f.readlines()

        content = ""
        for ycappuccino_component in list_ycappuccino_component:
            list_component_hierarchy = list(inspect.getmro(ycappuccino_component))
            list_matches = re.findall(
                f"class {ycappuccino_component.__name__}.*",
                "\n".join(content_original_file),
            )
            if list_matches is not None and len(list_matches) > 0:
                content_next, instance_name = await self.generate_component(
                    ycappuccino_component,
                    list_component_hierarchy,
                    module,
                )
                content = content + content_next
                res.append(
                    GeneratedComponent(
                        module_name=pelix_module_name,
                        instance_name=instance_name,
                        instance_name_obj=instance_name,
                        content=content,
                    )
                )
        return res

    def get_arg_new(self, all: list[list]) -> list[str]:
        args_new: list[str] = []
        for property in all:
            if property[-1]:
                prop = f"None if self.{property[0]} is None else  self.{property[0]}[0]._obj if  isinstance(self.{property[0]},list) else self.{property[0]}._obj"
            else:
                prop = f"self.{property[0]}"

            args_new.append(prop)
        return args_new

    async def generate_component(
        self,
        ycappuccino_component: type,
        list_ycappuccino_component: list[type],
        module: ModuleType,
    ) -> t.Tuple[str, str]:

        props = await self.get_requires_from_ycappuccino_component(
            ycappuccino_component, self._inspect_module
        )

        factory: str = ycappuccino_component.__name__ + "Factory"
        provides: str = '","'.join(
            [
                comp.__name__
                for comp in list_ycappuccino_component
                if comp.__name__ is not abc.ABC.__name__ and comp.__name__ != "object"
                if comp.__name__ not in props.get("requires_spec")  # type: ignore
                and comp.__name__ not in props.get("binds_spec")  # type: ignore
            ]
        )
        parameters: list[str] = []
        args_new: list[str] = self.get_arg_new(props.get("all"))  # type: ignore
        properties: list[str] = await self.get_dumps(
            kind="Property",
            parameter_dump=parameters,
            dec_tuple=props.get("properties"),  # type: ignore
        )
        requires: list[str] = await self.get_dumps(
            kind="Requires",
            parameter_dump=parameters,
            dec_tuple=props.get("requires"),  # type: ignore
        )
        bind_methods: list[str] = await self.get_bind_dumps(
            dec_tuple=props.get("binds"),  # type: ignore
        )

        content, instance_name = await self.get_pelix_module_str(
            bind_methods=bind_methods,
            requires=requires,
            properties=properties,
            parameters=parameters,
            ycappuccino_component=ycappuccino_component,
            factory=factory,
            provides=provides,
            module=module,
            args_new=args_new,
        )
        return content, instance_name

    @staticmethod
    async def get_pelix_module_str(
        bind_methods: list[str],
        requires: list[str],
        properties: list[str],
        parameters: list[str],
        ycappuccino_component: type,
        factory: str,
        provides: str,
        module: ModuleType,
        args_new: list[str],
    ) -> t.Tuple[str, str]:
        bind_methods_dump: str = "\n".join(bind_methods)
        requires_dump: str = "\n".join(requires)
        properties_dump: str = "\n".join(properties)
        parameter_dump: str = "\n        ".join(parameters)
        instance: str = "_".join([factory, str(datetime.now().timestamp())])
        args_new_dump = ",".join(args_new)
        class_new: str = f"{ycappuccino_component.__name__}({args_new_dump})"
        klass: str = ycappuccino_component.__name__
        return (
            f"""from pelix.ipopo.decorators import  BindField, UnbindField,Instantiate, Requires, Provides, ComponentFactory, Property, Validate, Invalidate
import asyncio
from ycappuccino.api.proxy import Proxy
from ycappuccino.api.executor_service import execute_async_in_thread
from {module.__name__} import {klass}


@ComponentFactory("{factory}")
@Provides(specifications=["{provides}"], controller="controller")
{requires_dump}
{properties_dump}
@Instantiate("{instance}")
class {factory}Ipopo(Proxy):

    def __int__(self):
        super().__init__()
        self._context = None
        self.controller = False
        {parameter_dump}
{bind_methods_dump}
    async def _start(self):
        await self._obj.start()
        self.controller = True

    async def _stop(self):
        await self._obj.stop()
        self.controller = False

    @Validate
    def validate(self, context):
        self._objname = "{instance}"
        self._obj = {class_new}
        self._obj._ipopo = self
        self._context = context
        execute_async_in_thread(self._start)

    @Invalidate
    def in_validate(self, context):
        execute_async_in_thread(self._stop)
        self._objname = None
        self._obj = None
        self._context = None
""",
            instance,
        )

    async def load_discovered(
        self, component_discovered: ComponentDiscovered
    ) -> Bundle:
        bundle = self.context.install_bundle(
            component_discovered.module_name, component_discovered.path
        )
        bundle.start()
        return bundle

    async def load_generated(self, component_generated: GeneratedComponent) -> Bundle:
        mymodule = ModuleType(component_generated.module_name)
        try:
            exec(component_generated.content, mymodule.__dict__)

            sys.modules[component_generated.module_name] = mymodule
            print(f"install bundle {component_generated.module_name}")
            bundle = self.context.install_bundle(component_generated.module_name)
            print(f"start bundle {component_generated.module_name}")
            bundle.start()

            return bundle
        except BaseException as e:
            print(f"error {e}")
            raise e

    async def loads(self) -> None:
        """
        load all component discovered
        """
        print("load all component discovered")
        for component_discovered in await self._component_repository.list():
            self.list_bundles.append(await self.load_discovered(component_discovered))
            print(f"load {component_discovered.module_name}")
            _list = await self.generate(component_discovered)
            for generate_component in _list:
                print(f"generate {generate_component.instance_name}")
                self.generated_components[generate_component.instance_name] = (
                    generate_component
                )
                print(f"load {generate_component.instance_name}")
                self.list_bundles.append(await self.load_generated(generate_component))
                print(f"load {generate_component.instance_name} done")
        print("load all component discovered done")
        self.controller = True

    @staticmethod
    async def get_requires_from_ycappuccino_component(
        component: type, inspect_module: IInspectModule
    ) -> dict[str, list[list]]:
        sign = inspect.signature(component.__init__)  # type: ignore
        binds: list[list] = []
        requires: list[list] = []

        if inspect_module.is_ycappuccino_component(component):
            # manage type of bind to generate bind method
            if "bind" in component.__dict__:
                sign_bind = inspect.signature(component.bind)  # type: ignore
                for key, item in sign_bind.parameters.items():
                    if key != "self":
                        if item.annotation.__name__ != "_UnionGenericAlias":
                            require = [
                                item.annotation.__name__.lower(),
                                item.annotation.__name__,
                                True,
                                True,
                                "",
                                True,
                            ]

                            requires.append(require)

                            elem = [
                                item.annotation.__name__.lower(),
                                item.annotation.__name__,
                            ]
                            binds.append(elem)
        properties: list[list] = []
        all: list[list] = []
        for key, item in sign.parameters.items():
            if item.default is not inspect._empty:  # type: ignore
                elem = [key, item.annotation.__name__, item.default, False]
                properties.append(elem)
                all.append(elem)

            else:
                options = False
                spec_filter = ""
                _type = None
                is_require = False
                if type(item.annotation).__name__ == "_UnionGenericAlias":
                    options = True
                    if item.annotation.__args__[0].__name__ == "YCappuccinoTypeDefault":
                        spec_filter = item.annotation.__args__[0].spec_filter
                        _type = item.annotation.__args__[0].type.__name__
                    else:
                        _type = item.annotation.__arg__[0].__name__
                    is_require = True

                elif item.annotation.__name__ == "YCappuccinoTypeDefault":
                    spec_filter = item.annotation.spec_filter
                    _type = item.annotation.type.__name__
                    is_require = True
                elif inspect_module.is_ycappuccino_component(item.annotation, True):
                    _type = item.annotation.__name__
                    is_require = True

                if _type:
                    require = [
                        key,
                        _type,
                        False,
                        options,
                        spec_filter,
                        is_require,
                    ]
                    requires.append(require)
                    all.append(require)
        return {
            "requires": requires,
            "properties": properties,
            "binds": binds,
            "all": all,
            "requires_spec": [require[1] for require in requires],
            "binds_spec": [bind[1] for bind in binds],
        }

    @staticmethod
    async def get_dumps(
        kind: str, dec_tuple: list[list], parameter_dump: list[str]
    ) -> list[str]:
        if dec_tuple is None:
            return []
        properties_dump: list[str] = []
        for prop in dec_tuple:
            if prop[-1]:
                properties_dump.append(
                    f'@{kind}("{prop[0]}", "{prop[1]}", optional={prop[2]},aggregate={prop[3]}, spec_filter="{prop[4]}")'
                )
            else:
                if kind == "Property":
                    properties_dump.append(
                        f'@{kind}("{prop[0]}","{prop[0]}","{prop[2]}")'
                    )
                else:
                    properties_dump.append(f'@{kind}("{prop[0]}","{prop[1]}")')
            parameter_dump.append(f"self.{prop[0]} = None")

        return properties_dump

    @staticmethod
    async def get_bind_dumps(dec_tuple: list[list]) -> list[str]:
        if dec_tuple is None:
            return []
        properties_dump: list[str] = []
        for prop in dec_tuple:
            properties_dump.append(
                f"""
    async def _bind(self,service):
        await  self._obj.bind(service)
        self.controller = True

    @BindField("{prop[0]}")
    def bind_{prop[0]}(self, field, service, service_ref):
        execute_async_in_thread(self._bind,service)

    async def _un_bind(self,service):
        await  self._obj.un_bind(service)
        self.controller = False

    @UnbindField("{prop[0]}")
    def un_bind_{prop[0]}(self, field, service, service_ref):
        execute_async_in_thread(self._un_bind,service)
"""
            )

        return properties_dump
