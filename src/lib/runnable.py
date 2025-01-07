import abc
import traceback
from typing import TypeVar

from typing_extensions import Generic
from typing import TYPE_CHECKING

from src.lib.exceptions import MisconfiguredTestClass, TestFailedToExecute

if TYPE_CHECKING:
    from src.lib.autobadger import AutobadgerCallback
from src.lib.types import AutobadgerResult, TestResult

T = TypeVar("T")


class Runnable(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def run(self) -> T:
        pass


class TestRunnable(Runnable[AutobadgerResult]):
    def __init__(self, callback: "AutobadgerCallback") -> None:
        super(TestRunnable, self).__init__()
        self.callback = callback

    def _get_test_method_names_of(self):
        return [fn_name for fn_name in dir(self) if fn_name.startswith("test_")]

    def run(self):
        total_possible_score = self.__class__.__points__
        grade = AutobadgerResult(project=self.__class__.__project__)
        test_fns = self._get_test_method_names_of()
        if len(test_fns) < 1:
            raise MisconfiguredTestClass(class_name=self.__class__.__name__)
        for test_fn in test_fns:
            self.callback.on_before_test()
            try:
                test_result: TestResult = getattr(self, test_fn)()
            except TestFailedToExecute as e:
                trace = "\n".join(
                    [
                        f"Failed to run Q{e.Q} ('{test_fn}'):",
                        traceback.format_exc(),
                    ]
                )
                test_result = TestResult.Zero(
                    question=test_fn,
                    total=e.total,
                    message=str(e.original_exception),
                    stack_trace=trace,
                    Q=e.Q,
                )
            self.callback.on_after_test()
            grade.add_test(test_result)
        assert (
            grade.score.total == total_possible_score
        ), f"Double check the scores of your tests and the total score for the class. {total_possible_score} != {grade.score.total}"
        return grade


RegisteredTestClass = type[Runnable[TestResult]]


"""
P2 EXAMPLE
{
  "score": 100,
  "full_score": 100,
  "tests": {
    "docker_build": "PASS (10/10)",
    "proto_compile": "PASS (10/10)",
    "servers_run": "PASS (5/5)",
    "client_runs": "PASS (5/5)",
    "test_input_0": "PASS (10/10)",
    "test_input_1": "PASS (20/20)",
    "test_input_2": "PASS (20/20)",
    "test_input_3": "PASS (20/20)"
  }
}

P3 EXAMPLE
{
   "score":45,
   "full_score":75,
   "tests":{
      "docker_build":"PASS (5/5)",
      "docker_run":"PASS (5/5)",
      "upload_test":"PASS (10/10)",
      "csvsum_test":"PASS (10/10)",
      "parquetsum_test":[
         "Traceback (most recent call last):\n",
         "  File \"/home/tareq/autograde/submissions/p3_mwzhang2/autograde.py\", line 65, in run\n    result = self.func()\n             ^^^^^^^^^^^\n",
         "  File \"/home/tareq/autograde/submissions/p3_mwzhang2/autograde.py\", line 529, in parquetsum_test\n    int_last_line = int(last_line)\n                    ^^^^^^^^^^^^^^\n",
         "ValueError: invalid literal for int() with base 10: '__filename: string'\n"
      ],
      "big_upload":"PASS (15/15)",
      "big_sum":[
         "Traceback (most recent call last):\n",
         "  File \"/home/tareq/autograde/submissions/p3_mwzhang2/autograde.py\", line 65, in run\n    result = self.func()\n             ^^^^^^^^^^^\n",
         "  File \"/home/tareq/autograde/submissions/p3_mwzhang2/autograde.py\", line 559, in big_sum\n    parquetsum = int(parquetsum_output.strip().split(\"\\n\")[-1])\n                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
         "ValueError: invalid literal for int() with base 10: '__filename: string'\n"
      ]
   }
}
"""
