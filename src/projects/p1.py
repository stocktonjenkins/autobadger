from ..lib.autobadger import Callback
from ..lib.enums import Project, Registry
from ..lib.registry import register, graded
from ..lib.runnable import TestRunnable
from ..lib.types import TestError


@register(project=Project.P1, registry=Registry.TEST, points=20)
class ProjectOneTest(TestRunnable):
    @graded(Q=1, points=10)
    def test_os(self) -> int | TestError:
        # return TestError(message="Expected ... but got ...", earned=5)
        return 10

    @graded(Q=2, points=10)
    def test_foo(self) -> int | TestError:
        return 10


@register(project=Project.P1, registry=Registry.CALLBACK)
class ProjectOneCallback(Callback):
    def on_setup(self):
        pass

    def on_teardown(self):
        pass

    def on_validate_required_resources(self):
        pass

    def on_before_test(self):
        pass

    def on_after_test(self):
        pass
