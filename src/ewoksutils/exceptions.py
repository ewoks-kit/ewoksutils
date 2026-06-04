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
