import warnings
from typing import Callable

from src.lib.autobadger import Callback
from src.lib.enums import Project, Registry, TestStatus
from src.lib.exceptions import TestFailedToExecute
from src.lib.runnable import RegisteredTestClass
from src.lib.types import TestResult, Score, RegisteredCallback, TestError

_test_registry: list[RegisteredTestClass] = []
_callback_registry: list[RegisteredCallback] = []


def register(project: Project, registry: Registry, points: int | None = None):
    def decorator(cls: RegisteredTestClass | RegisteredCallback):
        cls.__project__ = project
        if registry == Registry.TEST:
            assert points is not None, "assign total points for this class of tests"
            cls.__points__ = points
            _test_registry.append(cls)
        elif registry == Registry.CALLBACK:
            _callback_registry.append(cls)

    return decorator


def graded(Q: int, points: int):
    def decorator(func: Callable[[...], int | TestError]):
        def wrapper(*args, **kwargs) -> TestResult:
            name = func.__name__
            try:
                result = func(*args, **kwargs)
                if isinstance(result, int):
                    score = Score(earned=result, total=points)
                    return TestResult(
                        test_name=name,
                        status=TestStatus.from_score(score),
                        score=score,
                        Q=Q,
                    )
                elif isinstance(result, TestError):
                    score = Score(earned=result.earned, total=points)
                    result.message = f"Incorrect answer: {result.message}"
                    return TestResult(
                        test_name=name,
                        status=TestStatus.from_score(score),
                        score=score,
                        Q=Q,
                        error=result,
                    )
                else:
                    raise ValueError(
                        f"Invalid type returned from test '{name}': {type(result)}"
                    )
            except Exception as e:
                raise TestFailedToExecute(
                    test_name=name, original_exception=e, total=points, Q=Q
                ) from e

        return wrapper

    return decorator


def get_registry(
    project: Project, registry: Registry
) -> list[RegisteredTestClass] | list[Callback]:
    import importlib

    # TODO: validate this method would work when used as a PIP package
    importlib.import_module("src.projects")
    if registry == Registry.TEST:
        tests = list(filter(lambda cls: cls.__project__ == project, _test_registry))
        assert len(tests) > 0, f"No tests found for {project.value}!"
        return tests
    elif registry == Registry.CALLBACK:
        callbacks = list(
            filter(lambda cls: cls.__project__ == project, _callback_registry)
        )
        if len(callbacks) == 0:
            warnings.warn(f"No callbacks found for {project.value}!")
        return callbacks
