import abc

from ycappuccino.api.core import IRunner
from ycappuccino.core.framework import YCappuccino


class Runner(abc.ABC, IRunner):

    def __init__(self):
        self._framework = YCappuccino()

    def start(self) -> None:
        self._framework.start(yml_path="application.yaml")

    def stop(self) -> None:
        if self._framework is not None:
            self._framework.stop()


if __name__ == "__main__":
    runner = Runner()
    runner.start()
