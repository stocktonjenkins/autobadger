import re
from copy import deepcopy
from datetime import datetime
from functools import reduce
from typing import Callable

from pydantic import BaseModel, Field

from .enums import Project, TestStatus


class Score(BaseModel):
    earned: int
    total: int

    def __add__(self, other):
        self.earned += other.earned
        self.total += other.total
        return self

    def __str__(self):
        return f"({self.earned}/{self.total})"

    def to_dict(self) -> dict:
        return {"earned": self.earned, "total": self.total}


class TestError(BaseModel):
    message: str
    stacktrace: str | None = None
    earned: int = 0

    def __str__(self):
        return f"Original Error: {self.message}:\nStacktrace: {self.stacktrace}"

    def to_dict(self) -> dict:
        out = {
            "message": self.message,
        }
        if self.stacktrace is not None:
            out["stacktrace"] = [
                line.strip()
                for line in self.stacktrace.strip().split("\n")
                if line.strip() and not re.match(r"^(\^)*$", line.strip())
            ]
        return out


class TestResult(BaseModel):
    test_name: str
    Q: int
    status: TestStatus
    score: Score
    error: TestError | None = None

    @classmethod
    def Zero(
        cls, question: str, total: int, message: str, stack_trace: str, Q: int
    ) -> "TestResult":
        return cls(
            test_name=question,
            status=TestStatus.FAILED,
            score=Score(earned=0, total=total),
            error=TestError(message=message, stacktrace=stack_trace),
            Q=Q,
        )

    def to_dict(self) -> dict:
        out = {
            f"Q{self.Q}": {
                "test_name": self.test_name,
                "status": self.status.value,
                "score": self.score.to_dict(),
            }
        }
        if self.error:
            out[f"Q{self.Q}"]["error"] = self.error.to_dict()
        return out


class AutobadgerResult(BaseModel):
    created: datetime = datetime.now()
    project: Project | None = None
    score: Score | None = None
    tests: list[TestResult] = Field(default_factory=list)

    def to_dict(self) -> dict:
        assert len(set([test.Q for test in self.tests])) == len(
            self.tests
        ), "Multiple tests share the same question number."
        out = reduce(
            lambda acc, curr: {**acc, **curr},
            [test.to_dict() for test in self.tests],
        )
        return {
            "created": self.created.isoformat(),
            "project": self.project.value,
            "score": self.score.to_dict() if self.score else "MISSING",
            "tests": {key: out[key] for key in sorted(out)},
        }

    def add_test(self, test: TestResult):
        self.tests.append(test)
        if self.score is None:
            self.score = deepcopy(test.score)
        else:
            self.score += test.score

    def join(self, other: "AutobadgerResult"):
        if self.project is None:
            self.project = deepcopy(other.project)
        if self.score is None:
            self.score = deepcopy(other.score)
        else:
            self.score += other.score
        self.tests.extend(other.tests)

    @classmethod
    def Zero(cls, project: Project, stack_trace: str, total: int) -> "AutobadgerResult":
        return cls(
            project=project,
            score=Score(earned=0, total=total),
            tests=[
                TestResult(
                    test_name="FATAL",
                    status=TestStatus.FATAL,
                    score=Score(earned=0, total=total),
                    error=TestError(
                        message="An error occurred while running your code.",
                        stacktrace=stack_trace,
                    ),
                )
            ],
        )


Callback = Callable[[...], None]
RegisteredCallback = type[Callback]
