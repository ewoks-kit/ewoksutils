import logging
import logging.handlers
import queue


def cleanup_logger(name: str):
    """Cleanup and delete a global python logger"""
    logging._acquireLock()  # type: ignore
    try:
        # Remove reference from root
        logger = logging.root.manager.loggerDict.pop(name, None)
        if not isinstance(logger, logging.Logger):
            return
        # Remove references from place holders
        _cleanup_logger_instance(logger)
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
    finally:
        logging._releaseLock()  # type: ignore


def _cleanup_logger_instance(logger: logging.Logger):
    """Cleanup a python logger"""
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.QueueHandler):
            handler.acquire()
            try:
                q = handler.queue
                if isinstance(q, queue.Queue):
                    with q.mutex:
                        q.queue.clear()
            finally:
                handler.release()
