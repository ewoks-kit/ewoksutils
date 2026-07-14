import logging
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

    def handleError(self, record):
        if self._disconnect_on_error and self._connected():
            self._disconnect()
        super().handleError(record)

    def emit(self, record):
        try:
            if not self._connected():
                self._connect()
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
