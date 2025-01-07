import abc
import traceback

from lib.enums import Project
from lib.exceptions import MissingRequiredResource, MisconfiguredTestClass
from lib.runnable import Runnable, RegisteredTestClass
from lib.types import AutobadgerResult


class Callback(abc.ABC):
    @abc.abstractmethod
    def on_setup(self):
        pass

    @abc.abstractmethod
    def on_teardown(self):
        pass

    @abc.abstractmethod
    def on_validate_required_resources(self):
        """
        :throws MissingRequiredResource:
        :return:
        """
        pass

    @abc.abstractmethod
    def on_before_test(self):
        pass

    @abc.abstractmethod
    def on_after_test(self):
        pass


class AutobadgerCallback(Callback):
    def __init__(self, callbacks: list[Callback]):
        self.callbacks = callbacks

    def on_validate_required_resources(self):
        self._run_callbacks("on_validate_required_resources")

    def _run_callbacks(self, func_name):
        for cb in self.callbacks:
            getattr(cb, func_name)(self)

    def on_setup(self):
        self._run_callbacks("on_setup")

    def on_teardown(self):
        self._run_callbacks("on_teardown")

    def on_before_test(self):
        self._run_callbacks("on_before_test")

    def on_after_test(self):
        self._run_callbacks("on_after_test")


class Autobadger(Runnable[AutobadgerResult]):
    """ """

    callbacks: list["Callback"] = []

    def __init__(
        self,
        project: Project,
        tests: list[RegisteredTestClass],
        callback: AutobadgerCallback,
    ) -> None:
        super().__init__()
        self.project = project
        self.callback = callback
        self.tests = tests

    def run(self) -> AutobadgerResult:
        grade = AutobadgerResult(project=self.project)
        try:
            self.callback.on_validate_required_resources()
        except MissingRequiredResource as e:
            return AutobadgerResult.Zero(self.project, stack_trace=str(e))
        self.callback.on_setup()
        total_score = sum([Test.__points__ for Test in self.tests])
        try:
            for Test in self.tests:
                grade.join(Test(self.callback).run())
        except MisconfiguredTestClass as e:
            raise MisconfiguredTestClass(e.class_name) from None
        except Exception as e:
            trace = "\n".join([f"{e}:", "Full Stacktrace:", traceback.format_exc()])
            grade = AutobadgerResult.Zero(self.project, trace, total=total_score)
        finally:
            self.callback.on_teardown()
        return grade

    def __call__(self, *args, **kwargs) -> AutobadgerResult:
        return self.run()
