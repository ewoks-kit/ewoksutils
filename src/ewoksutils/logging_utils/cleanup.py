import logging
import logging.handlers
import queue
from contextlib import contextmanager
from typing import Generator


@contextmanager
def protect_logging_state() -> Generator[None, None, None]:
    """A context manager for thread-safe and fork-safe access to
    global logging data structures. It can be used recursively.
    """
    with logging._lock:
        yield


def cleanup_logger(name: str):
    """Cleanup and delete a global python logger."""
    with protect_logging_state():
        # Remove reference from root
        logger = logging.root.manager.loggerDict.pop(name, None)
        if not isinstance(logger, logging.Logger):
            return

        # Remove references from place holders
        for handler in logger.handlers:
            cleanup_handler(handler)
        for placeholder in list(logging.root.manager.loggerDict.values()):
            if isinstance(placeholder, logging.PlaceHolder):
                placeholder.loggerMap.pop(logger, None)

        # Remove references from children
        children = [
            name
            for name, child in list(logging.root.manager.loggerDict.items())
            if isinstance(child, logging.Logger) and child.parent is logger
        ]
        for child in children:
            cleanup_logger(child)

        # Remove local reference
        del logger


def cleanup_handler(handler: logging.Handler) -> None:
    """Cleanup and close a python log handler."""
    if isinstance(handler, logging.handlers.QueueHandler):
        handler.acquire()
        try:
            q = handler.queue
            if isinstance(q, queue.Queue):
                with q.mutex:
                    q.queue.clear()
        finally:
            handler.release()
    handler.close()
