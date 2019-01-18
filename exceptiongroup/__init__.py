"""Top-level package for exceptiongroup."""

from ._version import __version__

__all__ = ["ExceptionGroup", "split", "catch"]


class ExceptionGroup(BaseException):
    """An exception that contains other exceptions.

    Its main use is to represent the situation when multiple child tasks all
    raise errors "in parallel".

    Args:
      message (str): A description of the overall exception.
      exceptions (list): The exceptions.
      sources (list): For each exception, a string describing where it came
        from.

    Raises:
      TypeError: if any of the passed in objects are not instances of
          :exc:`BaseException`.
      ValueError: if the exceptions and sources lists don't have the same
          length.

    """

    def __init__(self, message, exceptions, sources):
        super().__init__(message)
        self.exceptions = list(exceptions)
        for exc in self.exceptions:
            if not isinstance(exc, BaseException):
                raise TypeError(
                    "Expected an exception object, not {!r}".format(exc)
                )
        self.message = message
        self.sources = list(sources)
        if len(self.sources) != len(self.exceptions):
            raise ValueError(
                "different number of sources ({}) and exceptions ({})".format(
                    len(self.sources), len(self.exceptions)
                )
            )

    # it's strange that copy.copy doesn't work for ExceptionGroup object
    # because it's inheritant from BaseException, but can't figure out why.
    # For now, add __copy__ method to make ExceptionGroup can be copied.
    def __copy__(self):
        return self.__class__(self.message, self.exceptions, self.sources)


from . import _monkeypatch
from ._tools import split, catch
