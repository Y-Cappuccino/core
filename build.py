#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "core"
default_task = "publish"


@init
def set_properties(project):
    project.set_property("core", False)  # default is True
    project.build_depends_on("pyyaml")
    project.build_depends_on("pytest")
    project.build_depends_on("asyncio")
    project.build_depends_on("pytest-asyncio")
