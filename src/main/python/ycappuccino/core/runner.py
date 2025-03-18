import abc
import asyncio

from ycappuccino.api.core import IRunner
from ycappuccino.core.framework import YCappuccino
from ycappuccino.core.services.component_runner import PelixComponentRunner


class Runner(abc.ABC, IRunner):

    def __init__(self):

        self._framework = YCappuccino(PelixComponentRunner())

    def start(self) -> None:
        asyncio.run(self._framework.start(yml_path="application.yaml"))

    def stop(self) -> None:
        if self._framework is not None:
            asyncio.run(self._framework.stop())


if __name__ == "__main__":
    runner = Runner()
    runner.start()
