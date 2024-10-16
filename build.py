#   -*- coding: utf-8 -*-
import os
import shutil

from pybuilder.core import depends, task, use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "ycappuccino_core"
default_task = "publish"


@init
def set_properties(project):
    project.set_property("core", False)  # default is True
    project.depends_on_requirements("requirements.txt")


@task("bundle_dependencies")
@depends("prepare")
def bundle_dependencies(project, logger):
    # Path to where dependencies are installed during build
    dependencies_dir = os.path.join(project.expand_path("$dir_target"), "dependencies")
    os.makedirs(dependencies_dir, exist_ok=True)

    # Copy all dependencies to the dependencies directory
    for dep in project.dependencies:
        dep_path = dep.project_file_path
        if dep_path and os.path.exists(dep_path):
            if os.path.isdir(dep_path):
                shutil.copytree(
                    dep_path, os.path.join(dependencies_dir, os.path.basename(dep_path))
                )
            else:
                shutil.copy(dep_path, dependencies_dir)

    # Include dependencies directory in the wheel
    project.get_property("wheel_include_dirs").append("dependencies")


use_plugin("python.install_dependencies")


@init
def additional_properties(project):
    # Ensure the dependencies are included in the wheel
    project.set_property("wheel_include_dirs", [])
