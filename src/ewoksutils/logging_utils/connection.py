import logging
import time
from abc import abstractmethod
from typing import Any


class ConnectionHandler(logging.Handler):
    """A python handler with a generic underlying connection. The
    only requirement is that the connection closes itself on garbage collection.
    """

    def __init__(self):
        super().__init__()
        self._connection = None
        self.closeOnError = False
        self._retry_time = None
        #
        # Exponential backoff parameters.
        #
        self._retry_start = 1.0
        self._retry_max = 30.0
        self._retry_factor = 2.0

    @abstractmethod
    def _connect(self, timeout=1) -> None:
        """This is called when no connection exists."""
        pass

    @abstractmethod
    def _disconnect(self) -> None:
        """This is called when a connection exists and is connected."""
        pass

    @abstractmethod
    def _serialize_record(self, record: logging.LogRecord) -> Any:
        """Convert a record to something that can be given to the connection."""
        pass

    @abstractmethod
    def _send_serialized_record(self, srecord: Any):
        """Send the output from `_serialize_record` to the connection."""
        pass

    def _connected(self) -> bool:
        return self._connection is not None

    def _ensure_connection(self) -> bool:
        if self._connected():
            return True
        now = time.time()
        if self._retry_time is not None and now < self._retry_time:
            return False
        self._connect()
        if self._connected():
            # Connection succeeded: no delay for next connection attempt
            self._retry_time = None
            return True
        # Connection failed: no next connection attempt before _retry_time
        if self._retry_time is None:
            self._retry_period = self._retry_start
        else:
            self._retry_period = self._retry_period * self._retry_factor
            if self._retry_period > self._retry_max:
                self._retry_period = self._retry_max
        self._retry_time = now + self._retry_period
        return False

    def handleError(self, record):
        if self.closeOnError and self._connected():
            self._disconnect()
        else:
            super().handleError(record)

    def emit(self, record):
        try:
            if self._ensure_connection():
                s = self._serialize_record(record)
                self._send_serialized_record(s)
        except Exception:
            self.handleError(record)

    def close(self):
        self.acquire()
        try:
            if self._connected():
                self._disconnect()
            super().close()
        finally:
            self.release()
