class MissingRequiredResource(Exception):
    def __init__(self, resources: list[str]):
        super().__init__(
            f"Missing the following required resource(s): {', '.join(resources)}"
        )


class MisconfiguredTestClass(Exception):
    def __init__(self, class_name: str):
        self.class_name = class_name
        super().__init__(
            f"{class_name} is missing tests. Prefix your test method names with 'test_'."
        )


class TestFailedToExecute(Exception):
    def __init__(
        self, test_name: str, original_exception: Exception, total: int, Q: int
    ):
        self.test_name = test_name
        self.original_exception = original_exception
        self.total = total
        self.Q = Q
        super().__init__(
            f"Test {test_name} ({total} point(s)) failed to execute. Original exception: {self.original_exception}"
        )
