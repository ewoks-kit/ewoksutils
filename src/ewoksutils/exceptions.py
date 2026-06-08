"""Task-related exceptions."""


class TaskError(Exception):
    """Base exception for all task-related errors.

    This exception should not be raised directly. Use one of the
    more specific exceptions below.
    """

    pass


class TaskExecutionError(TaskError, RuntimeError):
    """Raised when a task fails during execution.

    This exception is raised when the task's `run()` method or
    any code executed during task processing raises an exception.

    Multiple inheritance from `RuntimeError` ensures backward
    compatibility with code that catches `RuntimeError` during
    task execution.
    """

    pass


class TaskInputError(TaskError, ValueError):
    """Raised when task inputs are invalid or missing.

    This exception is raised when:
    - Required inputs are missing
    - Input values fail validation
    - Input types are incorrect

    Multiple inheritance from `ValueError` ensures backward
    compatibility with code that catches `ValueError` during
    task instantiation.
    """

    pass


class TaskWarning(UserWarning):
    """Base warning for all task-related warnings.

    This warning should not be raised directly. Use one of the
    more specific warnings below.
    """

    pass


class TaskInputWarning(TaskWarning):
    """Raised when task inputs have issues that do not prevent execution.

    This warning is raised when:
    - Input values are deprecated
    - Input types will change in future versions
    - Input values have non-critical issues

    Inherits from `TaskWarning` to allow catching all task-related
    warnings together.
    """

    pass
